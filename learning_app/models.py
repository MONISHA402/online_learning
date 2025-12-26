from django.db import models
from django.contrib.auth.models import User
import re
from urllib.parse import urlparse, parse_qs


# ---------------- COURSES & MODULES ----------------
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_paid = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)

    def get_progress_percentage(self):
        # For testing, return a fixed dummy value
        return 45 

class Module(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")

    def __str__(self):
        return self.title

class Video(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    youtube_url = models.URLField()  # non-nullable
    allow_embed = models.BooleanField(default=True)
    thumbnail_url = models.URLField(blank=True, null=True)  # important!

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        if "watch?v=" in self.youtube_url:
            video_id = self.youtube_url.split("watch?v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in self.youtube_url:
            video_id = self.youtube_url.split("/")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.youtube_url

    def get_thumbnail_url(self):
        if "watch?v=" in self.youtube_url:
            video_id = self.youtube_url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in self.youtube_url:
            video_id = self.youtube_url.split("/")[-1]
        else:
            return ""
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


    
# ---------------- ENROLLMENT & PROGRESS ----------------
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Important!

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"



# ---------------- REVIEWS ----------------
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"



# ---------------- PAYMENTS (RAZORPAY) ----------------
class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.status}"

class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='user_progress')
    progress_percentage = models.PositiveIntegerField(default=0)  # 0–100

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}: {self.progress_percentage}%"