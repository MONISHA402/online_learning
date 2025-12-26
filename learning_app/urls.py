from django.urls import path
from . import views

urlpatterns = [
    # Home & Courses
    path('', views.home_view, name='home'),
    path('courses/', views.courses_view, name='courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    # Enrollment & Payment
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('payment/<int:course_id>/', views.payment_view, name='payment'),
    path('payment-success/<int:course_id>/', views.payment_success_view, name='payment_success'),

    # User Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
]
