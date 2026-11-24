import pytest

from unittest.mock import Mock

from apps.applications import notification_services


pytestmark = pytest.mark.django_db


class TestEmailNotifications:

    def test_application_created_email_is_sent(
        self,
        application,
        monkeypatch,
    ):
        send_mail = Mock(return_value=1)

        monkeypatch.setattr(
            notification_services,
            "send_mail",
            send_mail,
        )

        monkeypatch.setattr(
            notification_services.transaction,
            "on_commit",
            lambda callback: callback(),
        )

        notification_services.notify_application_created(
            application
        )

        send_mail.assert_called_once()

        kwargs = send_mail.call_args.kwargs

        assert "application created" in kwargs["subject"].lower()
        assert kwargs["recipient_list"] == [
            application.user.email
        ]

    def test_status_changed_email_is_sent(
        self,
        application,
        monkeypatch,
    ):
        send_mail = Mock(return_value=1)

        monkeypatch.setattr(
            notification_services,
            "send_mail",
            send_mail,
        )

        monkeypatch.setattr(
            notification_services.transaction,
            "on_commit",
            lambda callback: callback(),
        )

        notification_services.notify_application_status_changed(
            application,
            "applied",
            "interview",
        )

        send_mail.assert_called_once()

        kwargs = send_mail.call_args.kwargs

        assert "status" in kwargs["subject"].lower()
        assert application.user.email in kwargs["recipient_list"]
        assert "interview" in kwargs["message"].lower()

    def test_email_failure_does_not_break_notification_creation(
        self,
        application,
        monkeypatch,
    ):
        send_mail = Mock(
            side_effect=RuntimeError("Email provider unavailable")
        )

        monkeypatch.setattr(
            notification_services,
            "send_mail",
            send_mail,
        )

        monkeypatch.setattr(
            notification_services.transaction,
            "on_commit",
            lambda callback: callback(),
        )

        notification = notification_services.notify_application_created(
            application
        )

        assert notification.pk is not None
        assert send_mail.called