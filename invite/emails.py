from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def invitation_url(invitation):
    return settings.SITE_BASE_URL + reverse('invite_landing', args=[invitation.token])


def send_invitation_email(invitation):
    url = invitation_url(invitation)
    send_mail(
        subject='You’re invited to join Voilà Champagne as a Wine House',
        message=(
            f'Hello{" " + invitation.contact_name if invitation.contact_name else ""},\n\n'
            f'You’ve been invited to list your wines on Voilà Champagne. Follow the link below to '
            f'create your account and set up your Wine House profile:\n\n{url}\n\n'
            f'This link is unique to you — previously entered information will be saved as you go, '
            f'so you can pick up where you left off at any time.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.contact_email],
    )


def send_completion_notification(invitation):
    company_name = invitation.company.legal_name if invitation.company else invitation.contact_email
    send_mail(
        subject=f'New Wine House ready for review: {company_name}',
        message=(
            f'{company_name} has completed onboarding and is ready for review.\n\n'
            f'Contact: {invitation.contact_email}\n'
            f'Review in the admin: {settings.SITE_BASE_URL}/admin/company/company/{invitation.company_id}/change/'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
    )
