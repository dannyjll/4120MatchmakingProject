from django.urls import path
from matchmaking.consumers import MatchmakingConsumer

websocket_urlpatterns = [
    path('ws/matchmaking/', MatchmakingConsumer.as_asgi()),
]
