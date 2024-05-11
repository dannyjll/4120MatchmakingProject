from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate


class Rank(models.Model):
    rank_title = models.CharField(max_length=30)

    def __str__(self):
        return self.rank_title


class EloInfo(models.Model):
    player = models.OneToOneField(User, null=True, on_delete=models.CASCADE, unique=True)
    elo = models.IntegerField(default=300, validators=[MaxValueValidator(2000), MinValueValidator(0)])
    online_status = models.BooleanField()

    ROOKIE = 'Rookie'
    CHALLENGER = 'Challenger'
    SEASONED_PLAYER = 'Seasoned Player'
    VETERAN = 'Veteran'
    MASTER = 'Master'

    RANK_CHOICES = [
        (ROOKIE, 'Rookie'),
        (CHALLENGER, 'Challenger'),
        (SEASONED_PLAYER, 'Seasoned Player'),
        (VETERAN, 'Veteran'),
        (MASTER, 'Master'),
    ]

    rank_tier = models.CharField(max_length=20, choices=RANK_CHOICES, default=ROOKIE)

    def calculate_rank_tier(self):
        """
        Calculate the rank tier based on Elo rating.
        """
        if self.elo <= 400:
            return self.ROOKIE
        elif self.elo <= 800:
            return self.CHALLENGER
        elif self.elo <= 1200:
            return self.SEASONED_PLAYER
        elif self.elo <= 1600:
            return self.VETERAN
        else:
            return self.MASTER

    def save(self, *args, **kwargs):
        """
        Override the save method to update rank tier when saving player object.
        """
        self.rank_tier = self.calculate_rank_tier()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.player.username + "\'s Elo Info"


class Match(models.Model):
    match_date = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField(User)

    def __str__(self):
        return str(self.pk) + ": Match PK"


class Result(models.Model):
    match_id = models.ForeignKey(Match, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    match_result = models.BooleanField()

    def __str__(self):
        return str(self.match_id) + ' | ' + str(self.user_id) + "\'s " + "Result"
