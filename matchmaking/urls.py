from . import views
from django.urls import path, re_path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from matchmaking.consumers import MatchmakingConsumer

app_name = 'matchmaking'

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('findmatch', views.findmatch, name='findmatch'),
    re_path(r'^home/$', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]