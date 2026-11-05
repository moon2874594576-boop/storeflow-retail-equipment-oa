from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Announcement, AnnouncementRead
from .serializers import (
    AnnouncementSerializer, AnnouncementListSerializer,
    AnnouncementCreateSerializer
)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.select_related('publisher', 'department').all()
    filterset_fields = ['priority', 'status', 'department']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return AnnouncementListSerializer
        elif self.action == 'create':
            return AnnouncementCreateSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        queryset = Announcement.objects.select_related('publisher', 'department').all()
        keyword = self.request.query_params.get('keyword', '')
        status_filter = self.request.query_params.get('status', '')
        priority = self.request.query_params.get('priority', '')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        announcement = self.get_object()
        if announcement.status != 0:
            return Response({'error': '只有草稿状态可以发布'}, status=status.HTTP_400_BAD_REQUEST)
        announcement.status = 1
        announcement.published_at = timezone.now()
        announcement.save()
        return Response(AnnouncementSerializer(announcement).data)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        announcement = self.get_object()
        if announcement.status != 1:
            return Response({'error': '只有已发布状态可以撤回'}, status=status.HTTP_400_BAD_REQUEST)
        announcement.status = 2
        announcement.save()
        return Response(AnnouncementSerializer(announcement).data)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        announcement = self.get_object()
        read_record, created = AnnouncementRead.objects.get_or_create(
            announcement=announcement,
            user=request.user
        )
        return Response({'is_read': True})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        published = Announcement.objects.filter(status=1)
        total = published.count()
        read_count = AnnouncementRead.objects.filter(
            announcement__in=published,
            user=request.user
        ).count()
        return Response({
            'total': total,
            'unread': total - read_count
        })

    @action(detail=False, methods=['get'])
    def my_published(self, request):
        queryset = Announcement.objects.filter(publisher=request.user)\
            .select_related('department')
        keyword = request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AnnouncementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AnnouncementListSerializer(queryset, many=True)
        return Response(serializer.data)
