from .forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout


def home(request):
    return render(request, 'home.html',
                  {'matchmaking': home})


def findmatch(request):
    return render(request, 'findmatch.html', {'findmatch': findmatch})

def display_ranks(request):
    return render(request, 'displayranks.html', {'display_ranks': display_ranks})

def logout_view(request):
    logout(request)
