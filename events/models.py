from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    registration_start = models.DateTimeField(default=timezone.now)
    results_published = models.BooleanField(default=False)

    def is_full(self):
        return self.capacity <= self.registrations.count()

    def has_started(self):
        event_datetime = datetime.combine(self.date, self.time)
        event_datetime = timezone.make_aware(event_datetime)
        return timezone.now() > event_datetime

    def has_ended(self):
        event_datetime = datetime.combine(self.date, self.time)
        event_datetime = timezone.make_aware(event_datetime)
        return timezone.now() > event_datetime

    def __str__(self):
        return self.title

    def prize_counts(self):
        return {
            '1st': self.registrations.filter(prize='1st').count(),
            '2nd': self.registrations.filter(prize='2nd').count(),
            '3rd': self.registrations.filter(prize='3rd').count()
        }

    def can_award_prizes(self):
        counts = self.prize_counts()
        return all(count <= 1 for count in counts.values()) and sum(counts.values()) < 3


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    token = models.CharField(max_length=10)
    prize = models.CharField(max_length=10, choices=[('', 'No Prize'), ('1st', '1st Prize'), ('2nd', '2nd Prize'), ('3rd', '3rd Prize')], default='')

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class FrontPageVideo(models.Model):
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='front_page_videos/')

    def __str__(self):
        return self.title

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_rating = models.CharField(max_length=20)
    content_relevance = models.CharField(max_length=30)
    speaker_evaluation = models.CharField(max_length=20)
    organization_rating = models.CharField(max_length=30)
    suggestions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"Feedback from {self.user.username} for {self.event.title}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='team_images/')

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f"Profile for {self.user.username}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

class CollegePoster(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='posters/')

    def __str__(self):
        return self.title
