from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ApprovalType, Approval, ApprovalRecord
from .serializers import (
    ApprovalTypeSerializer, ApprovalSerializer,
    ApprovalListSerializer, CreateApprovalSerializer, ApprovalRecordSerializer
)

class ApprovalTypeViewSet(viewsets.ModelViewSet):
    queryset = ApprovalType.objects.all()
    serializer_class = ApprovalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def all(self, request):
        types = ApprovalType.objects.all()
        serializer = ApprovalTypeSerializer(types, many=True)
        return Response(serializer.data)

class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.select_related('type', 'applicant', 'current_approver').all()
    filterset_fields = ['status', 'type']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ApprovalListSerializer
        elif self.action == 'create':
            return CreateApprovalSerializer
        return ApprovalSerializer

    def get_queryset(self):
        queryset = Approval.objects.select_related('type', 'applicant', 'current_approver').all()
        keyword = self.request.query_params.get('keyword', '')
        status_filter = self.request.query_params.get('status', '')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword))
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = CreateApprovalSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        approval = serializer.save()
        ApprovalRecord.objects.create(
            approval=approval,
            approver=request.user,
            action='cc',
            comment='发起审批'
        )
        result = ApprovalSerializer(approval).data
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        queryset = Approval.objects.filter(applicant=request.user)\
            .select_related('type', 'applicant', 'current_approver')
        keyword = request.query_params.get('keyword', '')
        status_filter = request.query_params.get('status', '')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword))
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApprovalListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ApprovalListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        queryset = Approval.objects.filter(
            current_approver=request.user,
            status='pending'
        ).select_related('type', 'applicant', 'current_approver')
        keyword = request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApprovalListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ApprovalListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != 'pending':
            return Response({'error': '审批单已处理'}, status=status.HTTP_400_BAD_REQUEST)
        if approval.current_approver != request.user:
            return Response({'error': '您不是当前审批人'}, status=status.HTTP_403_FORBIDDEN)
        
        comment = request.data.get('comment', '')
        ApprovalRecord.objects.create(
            approval=approval,
            approver=request.user,
            action='approve',
            comment=comment
        )
        approval.status = 'approved'
        approval.current_approver = None
        approval.save()
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != 'pending':
            return Response({'error': '审批单已处理'}, status=status.HTTP_400_BAD_REQUEST)
        if approval.current_approver != request.user:
            return Response({'error': '您不是当前审批人'}, status=status.HTTP_403_FORBIDDEN)
        
        comment = request.data.get('comment', '')
        ApprovalRecord.objects.create(
            approval=approval,
            approver=request.user,
            action='reject',
            comment=comment
        )
        approval.status = 'rejected'
        approval.current_approver = None
        approval.save()
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        approval = self.get_object()
        if approval.applicant != request.user:
            return Response({'error': '只有申请人可以撤回'}, status=status.HTTP_403_FORBIDDEN)
        if approval.status != 'pending':
            return Response({'error': '只能撤回待审批的单据'}, status=status.HTTP_400_BAD_REQUEST)
        
        approval.status = 'revoked'
        approval.current_approver = None
        approval.save()
        ApprovalRecord.objects.create(
            approval=approval,
            approver=request.user,
            action='cc',
            comment='撤回审批'
        )
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        approval = self.get_object()
        records = approval.records.select_related('approver').all()
        serializer = ApprovalRecordSerializer(records, many=True)
        return Response(serializer.data)
