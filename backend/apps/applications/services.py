import logging

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.applications.models import ApplicationStatusHistory


logger = logging.getLogger(__name__)


ALLOWED_STATUS_TRANSITIONS = {
    "applied": {
        "assessment",
        "interview",
        "rejected",
        "withdrawn",
    },
    "assessment": {
        "interview",
        "rejected",
        "withdrawn",
    },
    "interview": {
        "offer",
        "rejected",
        "withdrawn",
    },
    "offer": {
        "withdrawn",
    },
    "rejected": set(),
    "withdrawn": set(),
}


def validate_status_transition(current_status, new_status):
    """
    Validate whether a status transition is allowed.
    """

    if current_status == new_status:
        raise ValidationError({
            "status": "The application already has this status."
        })

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise ValidationError({
            "status": (
                f"Cannot change application status from "
                f"'{current_status}' to '{new_status}'."
            )
        })


@transaction.atomic
def record_status_change(
    application,
    old_status,
    new_status,
    changed_by,
    remarks="",
):
    """
    Create a status history record.
    """

    history = ApplicationStatusHistory.objects.create(
        application=application,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        remarks=remarks,
    )

    logger.info(
        "Application %s status changed from %s to %s by user %s",
        application.id,
        old_status,
        new_status,
        changed_by.id,
    )

    return history


@transaction.atomic
def change_application_status(
    application,
    new_status,
    changed_by,
    remarks="",
):
    """
    Validate, update and record status history atomically.
    """

    old_status = application.status

    validate_status_transition(
        current_status=old_status,
        new_status=new_status,
    )

    application.status = new_status
    application.save(update_fields=["status", "updated_at"])

    return record_status_change(
        application=application,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        remarks=remarks,
    )