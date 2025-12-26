from django.contrib import admin
from .models import Course, Module, Video, Enrollment, Review, Payment

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Video)
admin.site.register(Enrollment)
admin.site.register(Review)
admin.site.register(Payment)
