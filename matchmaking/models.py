from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.conf import settings


class Rank(models.Model):
    rank_title = models.CharField(max_length=30)


class EloInfo(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)
    elo = models.IntegerField()
    online_status = models.BooleanField()


# class User(AbstractUser):
#     elo = models.IntegerField(default=1000, validators=[
#             MaxValueValidator(2000),
#             MinValueValidator(0),
#         ])
#     online_status = models.BooleanField()
#     rank_id = models.ForeignKey(Rank, on_delete=models.CASCADE)


class Match(models.Model):
    match_date = models.DateTimeField(default=timezone.now)


class Result(models.Model):
    match_id = models.ForeignKey(Match, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    match_result = models.BooleanField()
