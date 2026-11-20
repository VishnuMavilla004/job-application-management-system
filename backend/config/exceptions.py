import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is None:
        logger.exception(
            "Unhandled API exception",
            exc_info=exc,
        )
        return None

    original_data = response.data

    if isinstance(original_data, dict):
        message = original_data.get(
            "detail",
            "Request failed.",
        )
    else:
        message = "Validation failed."

    response.data = {
        "success": False,
        "message": str(message),
        "errors": original_data,
    }

    return response
