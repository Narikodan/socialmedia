from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post
from django.conf import settings
import os

def index(request):
    if request.user.is_authenticated:
        posts = Post.objects.all()  # Retrieve all posts from the database
        success_message = messages.get_messages(request)

        context = {
            'posts': posts,
            'success_message': success_message
        }

        return render(request, 'myapp/index.html', context)
    return redirect('myapp:login')

def register(request):
    User = get_user_model()
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        mobile_number = request.POST.get('mobile_number', '')
        password = request.POST.get('password', '')
        username = request.POST.get('username', '')

        # Validate form data
        if not first_name or not last_name or not mobile_number or not password or not username:
            messages.error(request, 'Please fill in all fields.')
        elif User.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, 'Mobile number is already registered.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        else:
            # Create user
            user = User.objects.create_user(first_name=first_name, last_name=last_name, mobile_number=mobile_number,
                                            password=password, username=username)
            messages.success(request, 'User created successfully!')
            return redirect('myapp:index')

    return render(request, 'myapp/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('myapp:index')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'myapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('myapp:index')



@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')
        user = request.user
        post = Post(user=user, text=text, image=image)
        post.save()

        # Move the uploaded image file to the desired directory
        if image:
            new_file_path = os.path.join('post_images', image.name)
            new_file_path = os.path.join(settings.MEDIA_ROOT, new_file_path)
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            with open(new_file_path, 'wb') as new_file:
                for chunk in image.chunks():
                    new_file.write(chunk)

        return redirect('myapp:index')  # Redirect to the home page after successful post creation

    return render(request, 'myapp/post.html')

