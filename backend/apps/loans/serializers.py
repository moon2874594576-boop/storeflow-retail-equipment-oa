from django.utils import timezone
from rest_framework import serializers
from apps.users.models import User
from .models import Store, Category, Asset, LoanRequest, LoanEvent
from .services import available_actions, user_name, ACTION_LABELS


class StrictSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        writable = {name for name, field in self.fields.items() if not field.read_only}
        extra = set(data) - writable
        if extra:
            raise serializers.ValidationError({name: '该字段不能直接修改。' for name in extra})
        return super().to_internal_value(data)


class StoreSerializer(StrictSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(source='manager', queryset=User.objects.all(), allow_null=True, required=False)
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ['id', 'code', 'name', 'manager_id', 'manager_name']
        read_only_fields = ['id', 'manager_name']

    def get_manager_name(self, obj) -> str:
        return user_name(obj.manager) if obj.manager_id else ''


class AssetSerializer(StrictSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    borrower_name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ['id', 'code', 'name', 'serial_number', 'category_id', 'category_name', 'status', 'status_label', 'borrower_name', 'store_name', 'updated_at']
        read_only_fields = ['id', 'status', 'updated_at']

    def active(self, obj):
        if not hasattr(obj, '_active_loan'):
            obj._active_loan = obj.loan_requests.filter(status__in=['handover', 'borrowed', 'return_pending']).select_related('applicant__loan_profile', 'store').first()
        return obj._active_loan

    def get_borrower_name(self, obj) -> str:
        item = self.active(obj)
        return user_name(item.applicant) if item else ''

    def get_store_name(self, obj) -> str:
        item = self.active(obj)
        return item.store.name if item else ''


class EventSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    request_number = serializers.CharField(source='request.number', read_only=True, default='')
    asset_code = serializers.CharField(source='asset.code', read_only=True, default='')

    class Meta:
        model = LoanEvent
        fields = ['id', 'request_id', 'request_number', 'asset_code', 'actor_name', 'action', 'label', 'from_status', 'to_status', 'reason', 'created_at']

    def get_actor_name(self, obj) -> str:
        return user_name(obj.actor)

    def get_label(self, obj) -> str:
        return ACTION_LABELS.get(obj.action, obj.action)


class LoanSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    store_name = serializers.CharField(source='store.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    asset_code = serializers.CharField(source='asset.code', read_only=True, default='')
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = LoanRequest
        fields = ['id', 'number', 'applicant_id', 'applicant_name', 'store_id', 'store_name', 'category_id', 'category_name', 'purpose', 'due_date', 'status', 'status_label', 'asset_code', 'asset_id', 'created_at', 'updated_at', 'submitted_at', 'decided_at', 'returned_at', 'overdue', 'available_actions']

    def get_applicant_name(self, obj) -> str:
        return user_name(obj.applicant)

    def get_available_actions(self, obj) -> list[str]:
        return available_actions(self.context['request'].user, obj)


class LoanDetailSerializer(LoanSerializer):
    events = EventSerializer(many=True, read_only=True)

    class Meta(LoanSerializer.Meta):
        fields = LoanSerializer.Meta.fields + ['events']


class LoanInputSerializer(StrictSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all())
    purpose = serializers.CharField(max_length=1000, min_length=2, trim_whitespace=True)

    class Meta:
        model = LoanRequest
        fields = ['category_id', 'purpose', 'due_date']

    def validate_due_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError('预计归还日期不能早于今天。')
        return value
