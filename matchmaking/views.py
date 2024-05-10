from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from django.db.models import Count
from django.shortcuts import render
import json


def home(request):
    return render(request, 'home.html',
                  {'matchmaking': home})


def findmatch(request):
    return render(request, 'findmatch.html', {'findmatch': findmatch})

def display_ranks(request):
    return render(request, 'displayranks.html', {'display_ranks': display_ranks})

def usersgraph(request):
    return render(request, 'usersgraph.html', {'usersgraph': usersgraph})


def logout_view(request):
    logout(request)

def usersgraph(request):
    data = User.objects.annotate(date=TruncDay('date_joined')).values('date').annotate(count=Count('id')).order_by(
        'date')

    dates = [item['date'].strftime('%Y-%m-%d') for item in data]
    counts = [item['count'] for item in data]

    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
    }
    return render(request, 'usersgraph.html', context)
