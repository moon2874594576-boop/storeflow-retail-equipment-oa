from django.contrib import admin
from .models import ApprovalType, Approval, ApprovalRecord

@admin.register(ApprovalType)
class ApprovalTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'created_at']
    search_fields = ['name', 'code']

@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'applicant', 'status', 'current_approver', 'created_at']
    list_filter = ['status', 'type']
    search_fields = ['title']

@admin.register(ApprovalRecord)
class ApprovalRecordAdmin(admin.ModelAdmin):
    list_display = ['approval', 'approver', 'action', 'comment', 'created_at']
    list_filter = ['action']
