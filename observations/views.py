from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Observation
from .forms import ObservationForm
from django.db.models import Count
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

@method_decorator(login_required, name='dispatch')
class ObservationCreateView(CreateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'observations/submit.html'
    success_url = reverse_lazy('observation_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Observation submitted successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ObservationUpdateView(UpdateView):
    model = Observation
    form_class = ObservationForm
    template_name = 'observations/submit.html'
    success_url = reverse_lazy('observation_list')

    def get_queryset(self):
        return Observation.objects.filter(observer=self.request.user)

@method_decorator(login_required, name='dispatch')
class ObservationDeleteView(DeleteView):
    model = Observation
    success_url = reverse_lazy('observation_list')
    template_name = 'observations/observation_confirm_delete.html'

    def get_queryset(self):
        return Observation.objects.filter(observer=self.request.user)

def popular_observations(request):
    observations = Observation.objects.order_by('-community_validations')[:6]
    return render(request, 'popular_observations.html', {
        'popular_observations': observations
    })

@login_required
@require_POST
def validate_observation(request, pk):
    observation = get_object_or_404(Observation, pk=pk)
    user = request.user
    # Use community_validations integer field
    validated = request.session.get(f'validated_{pk}', False)
    if not validated:
        observation.community_validations += 1
        observation.save()
        request.session[f'validated_{pk}'] = True
        # Award badge to validator
        if not user.badge or 'Validator' not in user.badge:
            user.badge = (user.badge + ', ' if user.badge else '') + 'Validator'
            user.save()
        messages.success(request, 'Thank you for validating this observation!')
    else:
        messages.info(request, 'You have already validated this observation.')
    return HttpResponseRedirect(reverse('observation_list'))

# API Views
class ObservationListCreateAPI(generics.ListCreateAPIView):
    queryset = Observation.objects.all().order_by('-created_at')
    serializer_class = ObservationSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        suggestion, confidence = get_mock_ai_suggestion()
        serializer.save(user=self.request.user, ai_suggestion=suggestion, ai_confidence=confidence)

class ObservationDetailAPI(generics.RetrieveAPIView):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    permission_classes = [permissions.IsAuthenticated]

RAG_SNIPPETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'snippets.txt')
RAG_FAQ_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rag_knowledge_base', 'faq_examples.txt')

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:1.5b"  # or 'deepseek-r1' if available:b
# Helper to get context from knowledge base

def get_rag_context(query):
    with open(RAG_FAQ_PATH, encoding='utf-8') as f:
        lines = f.read().split('\n')
    for i, line in enumerate(lines):
        if line.lower().startswith('q:') and query.lower() in line.lower():
            if i+1 < len(lines) and lines[i+1].lower().startswith('a:'):
                return lines[i+1][2:].strip()
    with open(RAG_SNIPPETS_PATH, encoding='utf-8') as f:
        snippets = f.read().split('\n\n')
    for snippet in snippets:
        if query.lower().split()[0] in snippet.lower():
            return snippet.strip()
    return "Margalla Hills is rich in biodiversity."

# Advanced RAG with Ollama

def ollama_rag_qa(query):
    context = get_rag_context(query)
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer as an expert on Islamabad biodiversity:"
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
        return f"[LLM unavailable, fallback] {context}"

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def rag_qa_view(request):
    answer = None
    if request.method == 'POST':
        question = request.POST.get('question', '')
        answer = ollama_rag_qa(question)
    return render(request, 'observations/rag_qa.html', {'answer': answer})
