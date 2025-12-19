import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, ValueError):
        return JsonResponse(
            {'detail': str(exc), 'code': 400},
            json_dumps_params={'ensure_ascii': False},
            status=status.HTTP_400_BAD_REQUEST
        )
    logging.error(f'Unhandled exception: {exc}', exc_info=True)
    return exception_handler(exc, context)
