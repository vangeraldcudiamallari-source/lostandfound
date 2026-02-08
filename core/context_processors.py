# core/context_processors.py
from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        # Count messages not sent by the user that are still marked as unread
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_count': count}
    return {'unread_count': 0}