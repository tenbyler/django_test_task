from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, User


# this handles the data transfer and Profile creation
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# this allows to save profile image
@receiver(post_save, sender=User)
def create_profile(sender, instance, **kwargs):
    instance.profile.save()