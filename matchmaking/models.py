from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.conf import settings


class Rank(models.Model):
    rank_title = models.CharField(max_length=30)

    def __str__(self):
        return self.rank_title


class EloInfo(models.Model):
    player = models.OneToOneField(User, null=True, on_delete=models.CASCADE, unique=True)
    elo = models.IntegerField()
    online_status = models.BooleanField()

    def __str__(self):
        return self.player.username + "\'s Elo Info"


# class User(AbstractUser):
#     elo = models.IntegerField(default=1000, validators=[
#             MaxValueValidator(2000),
#             MinValueValidator(0),
#         ])
#     online_status = models.BooleanField()
#     rank_id = models.ForeignKey(Rank, on_delete=models.CASCADE)


class Match(models.Model):
    match_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.pk + ": Match PK"


class Result(models.Model):
    match_id = models.ForeignKey(Match, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    match_result = models.BooleanField()

    def __str__(self):
        return self.user_id + "\'s Match Result"
