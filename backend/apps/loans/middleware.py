import logging
import time
import uuid

logger = logging.getLogger('storeflow.http')


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid.uuid4().hex[:16]
        start = time.perf_counter()
        response = self.get_response(request)
        response['X-Request-ID'] = request.request_id
        if request.path.startswith('/api/'):
            logger.info('request_id=%s method=%s path=%s status=%s duration_ms=%.1f', request.request_id, request.method, request.path, response.status_code, (time.perf_counter()-start)*1000)
        return response
