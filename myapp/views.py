from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Comment, Post, ProfilePicture
from django.conf import settings
import os

import json
from django.http import JsonResponse

from django.http import JsonResponse

@login_required
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            action = 'unliked'
        else:
            post.likes.add(request.user)
            action = 'liked'

        response_data = {'success': True, 'action': action}
        return JsonResponse(response_data)

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def index(request):
    if request.user.is_authenticated:
        posts = Post.objects.all()
        success_message = messages.get_messages(request)

        # Calculate comment count for each post
        comment_counts = {post.id: Comment.get_comment_count_for_post(post.id) for post in posts}

        context = {
            'posts': posts,
            'success_message': success_message,
            'comment_counts': comment_counts,  # Add comment_counts to the context
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
def profile(request):
    user = request.user
    return render(request, 'myapp/profile.html', {'user': user})

@login_required
def other_profile(request,username=None):
    user = get_object_or_404(get_user_model(), username=username)
    return render(request, 'myapp/other_profile.html', {'user': user})



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

def upload_profile_picture(request):
    if request.method == 'POST':
        image = request.FILES['image']
        profile_picture = ProfilePicture.objects.create(user=request.user, image=image)
        return redirect('myapp:profile')
    return render(request, 'myapp/upload_profile_picture.html')

@login_required
def delete_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
@login_required
def notification_view(request):
    user = request.user
    posts = Post.objects.filter(user=user)
    
    notifications = []
    for post in posts:
        notification = {
            'title': post.get_like_notification(),
            'post': post
        }
        if notification['title']:
            notifications.append(notification)
    
    context = {
        'notifications': notifications
    }

    return render(request, 'myapp/notifications.html', context)

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Additional logic for displaying the post details
    # You can customize this view according to your requirements
    context = {
        'post': post
    }
    return render(request, 'myapp/post_detail.html', context)


@login_required
def comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'myapp/comments.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        user = request.user

        # Create a new comment object and save it to the database
        comment = Comment(user=user, post=post, text=text)
        comment.save()

        # Redirect back to the post detail page after adding the comment
        return redirect('myapp:comments', post_id=post_id)

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST' and comment.user == request.user:
        # Delete the comment from the database
        comment.delete()

        # Redirect back to the post detail page after deleting the comment
        return redirect('myapp:post_detail', post_id=comment.post.id)

    return JsonResponse({'success': False, 'error': 'Invalid request method or permission'})

