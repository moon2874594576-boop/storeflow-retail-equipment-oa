from django.contrib import admin
from .models import Announcement, AnnouncementRead

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'department', 'priority', 'status', 'published_at']
    list_filter = ['priority', 'status', 'department']
    search_fields = ['title', 'content']

@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at']
    list_filter = ['read_at']
