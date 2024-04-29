from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import EloInfo


@receiver(post_save, sender=User)
def create_eloinfo(sender, instance, created, **kwargs):
    if created:
        EloInfo.objects.create(player=instance, elo=1000, online_status=True)
