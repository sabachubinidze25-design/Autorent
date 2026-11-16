from django.conf import settings


def site(request):
    user = request.user if request.user.is_authenticated else None
    return {
        "current_user": user,
        "unread_count": user.notifications.filter(is_read=False).count() if user else 0,
        "support_email": settings.SUPPORT_EMAIL,
        "support_phone": settings.SUPPORT_PHONE,
    }
