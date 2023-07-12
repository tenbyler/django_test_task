from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.conf import settings
from users.models import User


def one_day_after():
    return timezone.now() + timedelta(1)

class Task(models.Model):
    OPEN = 1
    IN_PROGRESS = 2
    COMPLETED = 3
      
    TASK_STATUS = (
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=one_day_after)
    author = models.ForeignKey(User, on_delete=models.SET("deleted user"), related_name = "author")
    status = models.PositiveSmallIntegerField(choices=TASK_STATUS, default=OPEN)
    completer = models.ForeignKey(User, limit_choices_to={'role': User.COMPLETER}, on_delete=models.SET("deleted user"), 
                                  blank=True, null=True, verbose_name = "Completer", 
                                  related_name = "completer")
    date_completed = models.DateTimeField(blank=True, null=True)
    completion_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("task-detail", kwargs={"pk": self.pk})
    

