from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, authenticate, logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
from .serializers import UserRegisterSerializer, UserProfileSerializer, UserProfileAPISerializer
from .forms import UserRegisterForm, UserProfileForm, CustomLoginForm, CustomSignupForm
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponseRedirect

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_mail(
            'Welcome to BioScout!',
            'Thank you for registering.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileAPISerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        return super().get(request, *args, **kwargs)

# Web registration view
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_mail(
                'Welcome to BioScout!',
                'Thank you for registering.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Web login view
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})

# Web logout view
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

# Web profile view
def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your profile.')
        return redirect('login')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Split badges for template and trim whitespace
    badges = [b.strip() for b in request.user.badge.split(',')] if request.user.badge else []
    # Get user's observations
    user_observations = request.user.observations.all().order_by('-created_at')
    return render(request, 'users/profile.html', {
        'form': form, 
        'badges': badges, 
        'user_observations': user_observations
    })

def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'users/custom_login.html', {'form': form})

def custom_signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomSignupForm()
    return render(request, 'users/custom_signup.html', {'form': form})

def custom_logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

def set_language(request):
    if request.method == 'POST':
        lang = request.POST.get('lang', 'en')
        request.session['language'] = lang
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
