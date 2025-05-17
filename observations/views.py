from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Observation, CorrectionRequest
from .forms import ObservationForm, CorrectionRequestForm
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions
from .serializers import ObservationSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import random
import os
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from users.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
import timm
import torch
from PIL import Image
from torchvision import transforms
import tempfile
import csv

User = get_user_model()

# Mock AI suggestion function
MOCK_SPECIES = [
    ("House Sparrow", 0.92),
    ("Common Myna", 0.85),
    ("Indian Peafowl", 0.78),
    ("Jungle Babbler", 0.81),
    ("Red-vented Bulbul", 0.88),
]

def get_mock_ai_suggestion():
    return random.choice(MOCK_SPECIES)

class ObservationListView(ListView):
    model = Observation
    template_name = 'observations/list.html'
    context_object_name = 'observations'
    ordering = ['-created_at']
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

class ObservationDetailView(DetailView):
    model = Observation
    template_name = 'observations/observation_detail.html'
    context_object_name = 'observation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Load the iNaturalist model and label mapping once
try:
    inat_model = timm.create_model('vit_large_patch14_clip_336.laion2b_ft_augreg_inat21', pretrained=True)
    inat_model.eval()
    # Load label mapping (should be a list of species names, one per line)
    LABELS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'inat21_labels.txt')
    with open(LABELS_PATH, encoding='utf-8') as f:
        inat_labels = [line.strip() for line in f if line.strip()]
except Exception as e:
    inat_model = None
    inat_labels = []

inat_preprocess = transforms.Compose([
    transforms.Resize(384),
    transforms.CenterCrop(384),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

def get_species_ai_suggestion(image_path):
    if inat_model is not None and inat_labels:
        try:
            image = Image.open(image_path).convert('RGB')
            input_tensor = inat_preprocess(image).unsqueeze(0)
            with torch.no_grad():
                output = inat_model(input_tensor)
            predicted_class = output.argmax().item()
            species_name = inat_labels[predicted_class] if predicted_class < len(inat_labels) else f"Class {predicted_class}"
            confidence = torch.softmax(output, dim=1)[0, predicted_class].item()
            return (species_name, confidence)
        except Exception as e:
            pass  # fallback to mock
    return get_mock_ai_suggestion()

@method_decorator(login_required, name='dispatch')
class ObservationCreateView(CreateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'observations/submit.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Use real model if image is present
        if self.request.FILES.get('image'):
            image = self.request.FILES['image']
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.name)[-1]) as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            try:
                suggestion, confidence = get_species_ai_suggestion(temp_path)
            finally:
                os.remove(temp_path)
            form.instance.ai_suggestion = suggestion
            form.instance.ai_confidence = confidence
        else:
            suggestion, confidence = get_mock_ai_suggestion()
            form.instance.ai_suggestion = suggestion
            form.instance.ai_confidence = confidence
        messages.success(self.request, 'Observation submitted successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ObservationUpdateView(UpdateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'observations/submit.html'
    success_url = reverse_lazy('observation_list')

    def get_queryset(self):
        return Observation.objects.filter(user=self.request.user)

@method_decorator(login_required, name='dispatch')
class ObservationDeleteView(DeleteView):
    model = Observation
    success_url = reverse_lazy('home')
    template_name = 'observations/observation_confirm_delete.html'

    def get_queryset(self):
        return Observation.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Observation deleted successfully!')
        return super().delete(request, *args, **kwargs)

def popular_observations(request):
    observations = Observation.objects.order_by('-community_validations')[:6]
    return render(request, 'popular_observations.html', {
        'popular_observations': observations
    })

@login_required
@require_POST
def validate_observation(request, pk):
    observation = get_object_or_404(Observation, pk=pk)
    
    # Check if user is trying to validate their own observation
    if request.user == observation.user:
        messages.error(request, "You cannot validate your own observation.")
        return HttpResponseRedirect(reverse('observation_detail', args=[pk]))
    
    # Check if user has already validated this observation
    if request.session.get(f'validated_{pk}', False):
        messages.info(request, 'You have already validated this observation.')
        return HttpResponseRedirect(reverse('observation_detail', args=[pk]))
    
    # Process validation
    observation.community_validations += 1
    observation.save()
    request.session[f'validated_{pk}'] = True
    
    # Award badge to validator
    if not request.user.badge or 'Validator' not in request.user.badge:
        request.user.badge = (request.user.badge + ', ' if request.user.badge else '') + 'Validator'
        request.user.save()
    
    messages.success(request, 'Thank you for validating this observation!')
    return HttpResponseRedirect(reverse('observation_detail', args=[pk]))

# API Views
class ObservationListCreateAPI(generics.ListCreateAPIView):
    queryset = Observation.objects.all().order_by('-created_at')
    serializer_class = ObservationSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        image = self.request.FILES.get('image')
        if image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.name)[-1]) as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            try:
                suggestion, confidence = get_species_ai_suggestion(temp_path)
            finally:
                os.remove(temp_path)
        else:
            suggestion, confidence = get_mock_ai_suggestion()
        serializer.save(user=self.request.user, ai_suggestion=suggestion, ai_confidence=confidence)

class ObservationDetailAPI(generics.RetrieveAPIView):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    permission_classes = [permissions.IsAuthenticated]

RAG_SNIPPETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'snippets.csv')
RAG_FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'faq_examples.csv')

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"  # or 'deepseek-r1' if available:b
# Helper to get context from knowledge base

def get_rag_context(query):
    # First check FAQ examples
    with open(RAG_FAQ_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if query.lower() in row['Question'].lower():
                return row['Answer']
    
    # Then check biodiversity observations
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'biodiversity_observations.csv'), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        relevant_observations = []
        for row in reader:
            if (query.lower() in row['species_name'].lower() or 
                query.lower() in row['common_name'].lower() or 
                query.lower() in row['descriptive_notes'].lower()):
                relevant_observations.append(f"Species: {row['common_name']} ({row['species_name']}) - {row['descriptive_notes']}")
        if relevant_observations:
            return "\n".join(relevant_observations)
    
    # Finally check general knowledge snippets
    with open(RAG_SNIPPETS_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        relevant_snippets = []
        for row in reader:
            if query.lower() in row['Snippet'].lower():
                relevant_snippets.append(row['Snippet'])
        if relevant_snippets:
            return "\n\n".join(relevant_snippets)
    
    return "Margalla Hills is rich in biodiversity. The area supports diverse bird species, mammals, and plant life. For specific information, please try rephrasing your question."

# Advanced RAG with Ollama

def ollama_rag_qa(query):
    context = get_rag_context(query)
    prompt = f"""Context: {context}

Question: {query}

Answer as an expert on Islamabad biodiversity. If the context contains specific observations, include relevant details about species, locations, and behaviors. If the context contains general information, provide a comprehensive overview. Keep the answer concise and informative:"""
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '').strip()
        else:
            return f"[Ollama error: {response.status_code}] {context}"
    except Exception as e:
        return f"{context}"

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:1b"
SYSTEM_PROMPT = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

# Initialize once (for demo, in production use a persistent store)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url="http://localhost:11434")
llm = OllamaLLM(model=LLM_MODEL, base_url="http://localhost:11434", temperature=0.3, timeout=180)
vector_store = InMemoryVectorStore(embeddings)
prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

# Load your knowledge base (e.g., from text files)
def load_knowledge_base():
    kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'snippets.csv')
    with open(kb_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        docs = [Document(page_content=row['Snippet']) for row in reader]
    vector_store.add_documents(docs)

load_knowledge_base()

def ollama_rag_qa_web(question):
    docs = vector_store.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = prompt | llm
    return chain.invoke({"question": question, "context": context})

LIBRETRANSLATE_URL = "http://localhost:5000/translate"

def libretranslate(text, source_lang="auto", target_lang="ur"):
    try:
        response = requests.post(
            LIBRETRANSLATE_URL,
            data={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("translatedText", text)
        else:
            return text
    except Exception:
        return text

@csrf_exempt
def rag_qa_ajax(request):
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'No question provided.'}, status=400)
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []
        chat_history = request.session['chat_history']
        chat_history.append({'role': 'user', 'content': question})
        try:
            answer = ollama_rag_qa_web(question)
            user_lang = request.session.get('language', 'en')
            if user_lang == 'ur':
                translated = libretranslate(answer, source_lang="en", target_lang="ur")
                if translated != answer:
                    answer = translated
        except Exception as e:
            answer = f"[Error: {str(e)}] Please ensure Ollama is running."
        chat_history.append({'role': 'bot', 'content': answer})
        request.session['chat_history'] = chat_history
        return JsonResponse({'answer': answer, 'chat_history': chat_history})
    return JsonResponse({'error': 'Invalid request.'}, status=400)

@csrf_exempt
def rag_qa_view(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    chat_history = request.session['chat_history']
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            chat_history.append({'role': 'user', 'content': question})
            answer = ollama_rag_qa_web(question)
            user_lang = request.session.get('language', 'en')
            if user_lang == 'ur':
                translated = libretranslate(answer, source_lang="en", target_lang="ur")
                if translated != answer:
                    answer = translated
            chat_history.append({'role': 'bot', 'content': answer})
            request.session['chat_history'] = chat_history
    if request.GET.get('clear'):
        chat_history.clear()
        request.session['chat_history'] = chat_history
    return render(request, 'observations/rag_qa.html', {'chat_history': chat_history})

@login_required
def dashboard(request):
    # Get user's observations
    user_observations = Observation.objects.filter(user=request.user).order_by('-created_at')[:5]
    user_observations_count = Observation.objects.filter(user=request.user).count()
    
    # Get total validations received by user's observations
    total_validations = Observation.objects.filter(user=request.user).aggregate(
        total=Count('community_validations'))['total'] or 0
    
    # Get observations that need validation (excluding user's own observations and already validated ones)
    validated_observation_ids = [k.split('_')[1] for k in request.session.keys() if k.startswith('validated_')]
    observations_needing_validation = Observation.objects.exclude(
        user=request.user
    ).exclude(
        id__in=validated_observation_ids
    ).order_by('-created_at')[:5]
    
    # Get user's badge
    badge = request.user.badge if hasattr(request.user, 'badge') else 'Novice'
    
    context = {
        'user_observations': user_observations,
        'user_observations_count': user_observations_count,
        'total_validations': total_validations,
        'observations_needing_validation': observations_needing_validation,
        'badge': badge,
    }
    
    return render(request, 'observations/dashboard.html', context)

@login_required
def submit_correction_request(request, pk):
    observation = get_object_or_404(Observation, pk=pk)
    if request.user == observation.user:
        messages.error(request, "You cannot request a correction on your own observation.")
        return redirect('observation_detail', pk=pk)
    if request.method == 'POST':
        form = CorrectionRequestForm(request.POST)
        if form.is_valid():
            correction = form.save(commit=False)
            correction.observation = observation
            correction.requested_by = request.user
            correction.save()
            messages.success(request, "Correction request submitted.")
            return redirect('observation_detail', pk=pk)
    else:
        form = CorrectionRequestForm()
    return render(request, 'observations/submit_correction.html', {'form': form, 'observation': observation})

@login_required
def review_correction_request(request, pk, req_id, action):
    observation = get_object_or_404(Observation, pk=pk)
    correction = get_object_or_404(CorrectionRequest, pk=req_id, observation=observation)
    if request.user != observation.user:
        messages.error(request, "Only the observation owner can review correction requests.")
        return redirect('observation_detail', pk=pk)
    if correction.status != 'pending':
        messages.info(request, "This correction request has already been reviewed.")
        return redirect('observation_detail', pk=pk)
    if action == 'accept':
        correction.status = 'accepted'
        correction.reviewed_at = timezone.now()
        correction.save()
        messages.success(request, "Correction request accepted.")
    elif action == 'reject':
        correction.status = 'rejected'
        correction.reviewed_at = timezone.now()
        correction.save()
        messages.success(request, "Correction request rejected.")
    return redirect('observation_detail', pk=pk)

def observation_detail(request, pk):
    observation = get_object_or_404(Observation, pk=pk)
    
    # Get similar observations (same species, excluding current observation)
    similar_observations = Observation.objects.filter(
        species_name=observation.species_name
    ).exclude(
        pk=observation.pk
    ).order_by('-date_observed')[:5]
    
    # Check if user has already validated this observation
    has_validated = False
    if request.user.is_authenticated:
        has_validated = request.session.get(f'validated_{pk}', False)
    
    # Correction requests (only for owner)
    correction_requests = []
    if request.user.is_authenticated and request.user == observation.user:
        correction_requests = observation.correction_requests.all().order_by('-created_at')
    
    context = {
        'observation': observation,
        'similar_observations': similar_observations,
        'has_validated': has_validated,
        'can_validate': request.user.is_authenticated and request.user != observation.user and not has_validated,
        'correction_requests': correction_requests,
    }
    return render(request, 'observations/observation_detail.html', context)

def home(request):
    from django.db.models import Count, Sum
    from users.models import User
    from .models import Observation

    # Featured: top 5 by validations
    featured_observations = Observation.objects.order_by('-community_validations', '-created_at')[:5]
    # Batch featured observations into pairs
    featured_observation_pairs = [featured_observations[i:i + 2] for i in range(0, len(featured_observations), 2)]
    
    # Recent: latest 6
    recent_observations = Observation.objects.order_by('-created_at')[:6]

    # Top Validators: users who validated the most (by sum of validations on others' observations)
    top_validators = (
        User.objects.annotate(validations_count=Sum('observations__community_validations'))
        .order_by('-validations_count')[:5]
    )
    # Top Observers: users with most observations
    top_observers = (
        User.objects.annotate(observations_count=Count('observations'))
        .order_by('-observations_count')[:5]
    )
    context = {
        'featured_observation_pairs': featured_observation_pairs,
        'recent_observations': recent_observations,
        'top_validators': top_validators,
        'top_observers': top_observers,
    }
    return render(request, 'welcome.html', context)
