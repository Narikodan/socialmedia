from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from .models import Comment, FriendRequest, Post, ProfilePicture
from django.conf import settings
import os

import json
from django.http import JsonResponse

from django.http import JsonResponse

def logout_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('myapp:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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

        for post in posts:
            post.comment_count = Comment.objects.filter(post=post).count()

        context = {
            'posts': posts,
            'success_message': success_message,
        }

        return render(request, 'myapp/index.html', context)

    return redirect('myapp:login')




@logout_required
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

@logout_required
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
    print("entering profile.......")
    user = request.user
    return render(request, 'myapp/profile.html', {'user': user})

@login_required
def other_profile(request, username):
    user = get_object_or_404(User, username=username)

    # Check if the viewed profile user is a friend of the currently logged-in user
    is_friend_of_viewer = user.friends.filter(id=request.user.id).exists()

    # Check if there is a pending friend request from the currently logged-in user to the viewed profile user
    has_pending_friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=user, status='P').exists()

    

    context = {
        'user': user,
        'is_friend_of_viewer': is_friend_of_viewer,
        'has_pending_friend_request': has_pending_friend_request,
    }
    return render(request, 'myapp/other_profile.html', context)





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

        # Check if the user already has a profile picture
        existing_profile_picture = ProfilePicture.objects.filter(user=request.user).first()

        if existing_profile_picture:
            # If the user already has a profile picture, update it
            existing_profile_picture.image = image
            existing_profile_picture.save()
        else:
            # If the user doesn't have a profile picture, create a new one
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
    post_id=comment.post.id

    if request.method == 'POST' and comment.user == request.user:
        print("Deleting comment:", comment_id)
        comment.delete()

        # Redirect back to the post detail page after deleting the comment
        return redirect('myapp:comments', post_id)

    return JsonResponse({'success': False, 'error': 'Invalid request method or permission'})



from django.shortcuts import render
from chatapp.models import Room

@login_required
def chat_rooms(request):
    rooms = Room.objects.all()
    return render(request, "myapp/chat_rooms.html", {"rooms": rooms})

def chat_room(request, slug):
    room = Room.objects.get(slug=slug)
    return render(request, 'myapp/chat_room.html', {'room': room})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from chatapp.models import Room, ChatParticipant

from django.urls import reverse
from django.db.models import Q  # Import Q to perform complex queries

@login_required
def chat_select_user(request):
    available_users = get_user_model().objects.exclude(id=request.user.id).exclude(
        chats__room__in=ChatParticipant.objects.filter(user=request.user).values('room')
    )

    if request.method == 'POST':
        selected_user_id = request.POST.get('user_id')
        if selected_user_id:
            selected_user = get_user_model().objects.get(id=selected_user_id)

            # Sort usernames alphabetically to ensure consistent room name
            usernames = sorted([request.user.username, selected_user.username])
            room_name = "_".join(usernames)

            # Check if a room already exists with both the logged-in user and the selected user
            existing_room = Room.objects.filter(
                Q(chat_participants__user=request.user) & Q(chat_participants__user=selected_user)
            ).first()

            if existing_room:
                # If a room already exists, redirect to that room
                room_url = reverse('chatapp:room', kwargs={'slug': existing_room.slug})
                return redirect(room_url)
            else:
                # If no room exists, create a new room and add the participants
                room, created = Room.objects.get_or_create(name=room_name)
                if created:
                    ChatParticipant.objects.create(user=request.user, room=room)
                    ChatParticipant.objects.create(user=selected_user, room=room)

                # Redirect to the new chat room
                room_url = reverse('chatapp:room', kwargs={'slug': room.slug})
                return redirect(room_url)

    return render(request, 'myapp/chat_select_user.html', {'available_users': available_users})


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if not request.user.friends.filter(id=user_id).exists() and not request.user.sent_friend_requests.filter(to_user=to_user).exists():
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            return redirect('myapp:other_profile', username=to_user.username)
        elif request.user.sent_friend_requests.filter(to_user=to_user).exists():
            FriendRequest.objects.filter(from_user=request.user, to_user=to_user).delete()
            return redirect('myapp:other_profile', username=to_user.username)
    return redirect('myapp:other_profile', username=to_user.username)

@login_required
def cancel_friend_request(request, user_id):
    if request.method == 'POST':
        to_user = get_object_or_404(get_user_model(), id=user_id)

        # Find the friend request from the current user to the to_user and delete it
        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=to_user).first()
        if friend_request:
            friend_request.delete()
            messages.success(request, 'Friend request canceled.')
            # You can implement sending notifications here if desired

    return redirect('myapp:profile')


@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

        # Add the sender to the current user's friends and vice versa
        request.user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(request.user)

        # Delete the friend request after accepting
        friend_request.delete()

        messages.success(request, 'Friend request accepted!')
        # You can implement sending notifications here if desired

    return redirect('myapp:friend_requests')

@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

        # Delete the friend request
        friend_request.delete()

        messages.success(request, 'Friend request rejected.')
        # You can implement sending notifications here if desired

    return redirect('myapp:friend_requests')

@login_required
def view_friend_requests(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user, status='P')

    # Calculate total number of friends for the logged-in user
    total_friends = request.user.friends.count()

    # Calculate count of friend requests for the logged-in user
    friend_requests_count = friend_requests.count()

    context = {
        'friend_requests': friend_requests,
        'total_friends': total_friends,
        'friend_requests_count': friend_requests_count,
    }
    return render(request, 'myapp/friend_requests.html', context)



from django.db.models import Q

@login_required
def unfriend_user(request, user_id):
    if request.method == 'POST':
        to_user = get_object_or_404(User, id=user_id)

        # Check if the users are friends before unfriending
        if request.user.friends.filter(id=user_id).exists() and to_user.friends.filter(id=request.user.id).exists():
            # Remove the friend connection
            request.user.friends.remove(to_user)
            to_user.friends.remove(request.user)

            # Delete existing friend requests (both sent and received) between the users
            FriendRequest.objects.filter(Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)).delete()

            messages.success(request, 'You have unfriended the user.')
            # You can implement sending notifications here if desired

    return redirect('myapp:other_profile', username=to_user.username)
