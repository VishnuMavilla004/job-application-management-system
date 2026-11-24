import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from apps.applications.models import ApplicationNotification


logger = logging.getLogger(__name__)


def create_application_notification(
    *,
    user,
    application,
    notification_type,
    title,
    message,
    email_subject,
    email_message,
):
    """
    Persist an in-app notification and send its email after commit.

    Email failure must not roll back a successfully saved application.
    """

    notification = ApplicationNotification.objects.create(
        user=user,
        application=application,
        notification_type=notification_type,
        title=title,
        message=message,
    )

    recipient_email = user.email

    def send_notification_email():
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )

            logger.info(
                "Notification email sent to %s for application %s",
                recipient_email,
                application.id if application else None,
            )

        except Exception:
            logger.exception(
                "Notification email failed for user %s",
                user.id,
            )

    transaction.on_commit(send_notification_email)

    return notification


def notify_application_created(application):
    user = application.user

    title = "Application created"

    message = (
        f"Your application for {application.job_title} "
        f"at {application.company.name} has been added successfully."
    )

    return create_application_notification(
        user=user,
        application=application,
        notification_type=(
            ApplicationNotification.NotificationType.APPLICATION_CREATED
        ),
        title=title,
        message=message,
        email_subject="Job application created successfully",
        email_message=(
            f"Hello {user.first_name or 'there'},\n\n"
            f"Your job application has been recorded.\n\n"
            f"Company: {application.company.name}\n"
            f"Position: {application.job_title}\n"
            f"Status: {application.status}\n\n"
            "You can review it in your Job Application Management System."
        ),
    )


def notify_application_status_changed(
    application,
    old_status,
    new_status,
):
    user = application.user

    title = "Application status updated"

    message = (
        f"Your application for {application.job_title} "
        f"at {application.company.name} changed from "
        f"{old_status} to {new_status}."
    )

    return create_application_notification(
        user=user,
        application=application,
        notification_type=(
            ApplicationNotification.NotificationType.STATUS_CHANGED
        ),
        title=title,
        message=message,
        email_subject="Your job application status has changed",
        email_message=(
            f"Hello {user.first_name or 'there'},\n\n"
            "Your application status has been updated.\n\n"
            f"Company: {application.company.name}\n"
            f"Position: {application.job_title}\n"
            f"Previous status: {old_status}\n"
            f"New status: {new_status}\n\n"
            "Log in to your Job Application Management System "
            "to view the latest details."
        ),
    )