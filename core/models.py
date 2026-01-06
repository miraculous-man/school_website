from django.db import models
from django.contrib.auth.models import User


class AcademicSession(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    TERM_CHOICES = [
        ('First', 'First Term'),
        ('Second', 'Second Term'),
        ('Third', 'Third Term'),
    ]
    name = models.CharField(max_length=20, choices=TERM_CHOICES)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.session.name}"


class ClassLevel(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    class_levels = models.ManyToManyField(ClassLevel, related_name='subjects')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class")

    def __str__(self):
        return self.name


class SubjectVideo(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(help_text="YouTube video URL")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.subject.name} - {self.title}"

    @property
    def youtube_embed_url(self):
        if 'youtube.com/watch?v=' in self.youtube_url:
            video_id = self.youtube_url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in self.youtube_url:
            video_id = self.youtube_url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.youtube_url


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200, default="My School")
    school_address = models.TextField(blank=True)
    school_phone = models.CharField(max_length=20, blank=True)
    school_email = models.EmailField(blank=True)
    school_logo = models.ImageField(upload_to='school/', blank=True, null=True)
    school_motto = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "School Settings"

    def __str__(self):
        return self.school_name
