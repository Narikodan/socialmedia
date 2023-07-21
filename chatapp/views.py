from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message

@login_required
def rooms(request):
    rooms = Room.objects.all()
    return render(request, "rooms.html", {"rooms": rooms})

@login_required
def chat_room(request, slug):
    try:
        room = Room.objects.get(slug=slug)
        room_name = room.name
        messages = Message.objects.filter(room=room)
        print(room.slug)
        return render(request, "room.html", {"room_name": room_name, "slug": slug, "messages": messages})
    except Room.DoesNotExist:
        # Handle the case when the room with the provided slug does not exist
        return render(request, "room_not_found.html")
