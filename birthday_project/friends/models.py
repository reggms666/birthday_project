from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)  # Временно разрешаем NULL
    birth_date = models.DateField(null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_code = models.CharField(
        max_length=16, unique=True, default=uuid.uuid4().hex[:16]
    )

    def __str__(self):
        return f'{self.user.username} (Telegram: {self.telegram_id})'

class Friend(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    birthday = models.DateField()

    def __str__(self):
        return f'{self.name} ({self.birthday})'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()