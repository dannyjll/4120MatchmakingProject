from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Match, Result, Rank, User, EloInfo

admin.site.register(Match)
admin.site.register(Result)
admin.site.register(Rank)
admin.site.register(EloInfo)
