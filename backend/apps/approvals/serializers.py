from rest_framework import serializers
from .models import ApprovalType, Approval, ApprovalRecord

class ApprovalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalType
        fields = ['id', 'name', 'code', 'description', 'fields', 'approvers', 'created_at']
        read_only_fields = ['created_at']

class ApprovalRecordSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ApprovalRecord
        fields = ['id', 'approval', 'approver', 'approver_name', 'action', 'action_display', 
                  'comment', 'created_at']
        read_only_fields = ['created_at']

class ApprovalSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    current_approver_name = serializers.CharField(source='current_approver.username', read_only=True, default='')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    records = ApprovalRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Approval
        fields = ['id', 'type', 'type_name', 'title', 'content', 'applicant', 'applicant_name',
                  'status', 'status_display', 'current_approver', 'current_approver_name',
                  'records', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ApprovalListSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Approval
        fields = ['id', 'type', 'type_name', 'title', 'applicant', 'applicant_name',
                  'status', 'status_display', 'created_at']

class CreateApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ['type', 'title', 'content']

    def validate(self, attrs):
        approval_type = attrs.get('type')
        if approval_type and approval_type.approvers:
            approvers = approval_type.approvers
            if approvers:
                attrs['current_approver_id'] = approvers[0] if approvers else None
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['applicant'] = user
        return super().create(validated_data)
