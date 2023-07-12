from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image


class User(AbstractUser):
    CREATOR = 1
    COMPLETER = 2
    
    ROLE_CHOICES = (
        (CREATOR, 'Creator'),
        (COMPLETER, 'Completor'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=False, null=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            img.thumbnail((300, 300))
            img.save(self.image.path)
