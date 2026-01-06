from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Notification, Announcement


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_POST
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


@login_required
def get_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_recent_notifications(request):
    notifications = Notification.objects.filter(user=request.user)[:5]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message[:100],
        'type': n.notification_type,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
    } for n in notifications]
    return JsonResponse({'notifications': data})


def create_notification(user, title, message, notification_type='info', link=''):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )


@login_required
def announcement_list(request):
    now = timezone.now()
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
    else:
        role = 'student'
    
    role_map = {
        'student': 'students',
        'teacher': 'teachers',
        'parent': 'parents',
        'admin': 'all',
        'accountant': 'staff',
        'librarian': 'staff',
    }
    
    audience = role_map.get(role, 'students')
    
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        models.Q(audience='all') | models.Q(audience=audience)
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    )
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'notifications/announcement_list.html', context)
