from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class JournalEntry (models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    sentiment_label = models.CharField(max_length=20, blank=True)
    sentiment_score = models.FloatField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"entry by {self.user.username} on {self.created_at}"

class Deadline(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.due_date}"



class Profile(models.Model):
    

    THEME_CHOICES = [
        ('light','☁️ daylight'),
        ('dark','🌑 midnight'),
        ('pastel','🌸 blossom'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light')

    reminder_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

