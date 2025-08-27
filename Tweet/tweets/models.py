# models.py
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

class Profile(models.Model):
    TOPIC_CHOICES = (
        ('anime', 'Anime'),
        ('study', 'Study'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('nature', 'Nature'),
        ('beauty', 'Beauty'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gener = MultiSelectField(choices=TOPIC_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Tweet(models.Model):
    TOPIC_CHOICES = (
    ('anime', 'Anime'),
    ('study', 'Study'),
    ('science', 'Science'),
    ('technology', 'Technology'),
    ('nature', 'Nature'),
    ('beauty', 'Beauty'),
    # add more...
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=100)
    text = models.TextField()
    photo = models.FileField(upload_to='photos/')
    content=models.TextField()
    gener = MultiSelectField(choices=TOPIC_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.user.username} - {self.text[:20]}'
    

class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.tweet}"

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="reactions")
    tweet = models.ForeignKey(Tweet, related_name='reactions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')  # so user can like once only

