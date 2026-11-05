from rest_framework import serializers
from .models import Announcement, AnnouncementRead

class AnnouncementSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    read_count = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'publisher', 'publisher_name',
                  'department', 'department_name', 'priority', 'priority_display',
                  'status', 'status_display', 'published_at', 'created_at',
                  'read_count', 'is_read']
        read_only_fields = ['publisher', 'published_at', 'created_at']

    def get_read_count(self, obj):
        return obj.reads.count()

    def get_is_read(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.reads.filter(user=user).exists()
        return False

class AnnouncementListSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'publisher_name', 'department_name',
                  'priority', 'priority_display', 'published_at', 'is_read']

    def get_is_read(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.reads.filter(user=user).exists()
        return False

class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'department', 'priority']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['publisher'] = user
        return super().create(validated_data)
