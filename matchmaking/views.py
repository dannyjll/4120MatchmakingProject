from .forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout


def home(request):
    return render(request, 'home.html',
                  {'matchmaking': home})


def logout_view(request):
    logout(request)
