import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Middleware para registrar todas las peticiones HTTP"""
    start_time = time.time()
    
    logger.info(f"➡️  {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"⬅️  {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.2f}s"
    )
    
    return response
