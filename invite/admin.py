from django.contrib import admin

from invite.emails import send_invitation_email
from invite.models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('contact_email', 'contact_name', 'status', 'step', 'company', 'user', 'created')
    list_filter = ('status', 'step')
    search_fields = ('contact_email', 'contact_name')
    fields = ('contact_email', 'contact_name', 'status', 'expires_at', 'invited_by', 'user', 'company', 'step', 'token', 'completed_at')
    readonly_fields = ('token', 'user', 'company', 'step', 'completed_at')
    actions = ['resend_invitation']

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        if is_new and not obj.invited_by_id:
            obj.invited_by = request.user
        super().save_model(request, obj, form, change)
        if is_new:
            send_invitation_email(obj)
            self.message_user(request, f'Invitation sent to {obj.contact_email}.')

    @admin.action(description='Resend invitation email')
    def resend_invitation(self, request, queryset):
        for invitation in queryset:
            send_invitation_email(invitation)
        self.message_user(request, f'Resent {queryset.count()} invitation(s).')
