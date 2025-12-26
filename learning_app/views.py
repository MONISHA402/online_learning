from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import ReviewForm
from django.shortcuts import render

from .models import Course, Module, Video, Enrollment, Review, Payment,UserCourseProgress


import razorpay

# Razorpay Client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# ---------------- USER AUTH ----------------

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful")
        return redirect('login')

    return render(request, 'learning_app/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'learning_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'learning_app/profile.html')


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("profile")
    return render(request, "learning_app/edit_profile.html", {"user": user})


# ---------------- COURSES ----------------

def home_view(request):
    courses = Course.objects.all()[:4]  # Show 4 courses on home
    return render(request, 'learning_app/home.html', {'courses': courses})


def courses_view(request):
    courses = Course.objects.all()
    return render(request, 'learning_app/courses.html', {'courses': courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.prefetch_related('videos')
    reviews = course.reviews.all()  # if you have a Review model
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(student=request.user).first()

    return render(request, 'learning_app/course_detail.html', {
        'course': course,
        'modules': modules,
        'reviews': reviews,
        'user_review': user_review,
    })


# ---------------- ENROLLMENT ----------------

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    # 🔥 THIS LINE FIXES DASHBOARD
    UserCourseProgress.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, "Successfully enrolled!")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return redirect('my_courses')



# ---------------- PAYMENT ----------------

@login_required
def payment_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    amount_in_paise = int(course.price * 100)

    order = client.order.create({
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1'
    })

    context = {
        'course': course,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': order['id'],
        'amount_in_paise': amount_in_paise,
    }
    return render(request, 'learning_app/payment.html', context)


@login_required
def payment_success_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    payment_id = request.GET.get('payment_id')  # Razorpay sends this

    if not payment_id:
        messages.error(request, "Payment failed: payment ID missing")
        return redirect('courses')

    # Save payment
    Payment.objects.create(
        student=request.user,
        course=course,
        payment_id=payment_id,
        status='Success'
    )

    # Enroll user
    Enrollment.objects.get_or_create(student=request.user, course=course)

    messages.success(request, "Payment successful and course enrolled!")
    return redirect('my_courses')


# ---------------- DASHBOARD & MY COURSES ----------------

@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')

    courses = []
    progress_dict = {}

    for enrollment in enrollments:
        course = enrollment.course
        courses.append(course)

        progress = UserCourseProgress.objects.filter(user=request.user, course=course).first()
        if progress:
            progress_dict[course.id] = progress.progress_percentage
        else:
            # Use model's dummy method if no progress exists
            progress_dict[course.id] = course.get_progress_percentage()

    return render(request, 'learning_app/dashboard.html', {
        'courses': courses,
        'progress_dict': progress_dict,
    })



@login_required
def my_courses_view(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'learning_app/my_courses.html', {'enrollments': enrollments})
