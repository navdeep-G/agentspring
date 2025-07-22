import logging
import logging.handlers
import os
import socket
from pythonjsonlogger import jsonlogger

LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'agentspring.log')
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 log files

os.makedirs(LOG_DIR, exist_ok=True)

class ContextFilter(logging.Filter):
    def __init__(self, user=None, request_id=None, error_type=None, tenant_id=None):
        super().__init__()
        self.user = user
        self.request_id = request_id
        self.error_type = error_type
        self.tenant_id = tenant_id
        self.environment = os.getenv('AGENTSPRING_ENV', 'development')
        self.hostname = socket.gethostname()

    def filter(self, record):
        record.user = getattr(record, 'user', self.user)
        record.request_id = getattr(record, 'request_id', self.request_id)
        record.error_type = getattr(record, 'error_type', self.error_type)
        record.tenant_id = getattr(record, 'tenant_id', self.tenant_id)
        record.environment = getattr(record, 'environment', self.environment)
        record.hostname = getattr(record, 'hostname', self.hostname)
        return True

class ScrubFilter(logging.Filter):
    SENSITIVE_KEYS = ['password', 'token', 'secret', 'api_key', 'authorization']
    MASK = '***REDACTED***'
    def filter(self, record):
        msg = record.getMessage()
        for key in self.SENSITIVE_KEYS:
            if key in msg.lower():
                msg = self._mask_key(msg, key)
        record.msg = msg
        return True
    def _mask_key(self, msg, key):
        import re
        # Mask key-value pairs like key=..., key: ..., "key": ...
        patterns = [
            rf'{key}\s*[=:]\s*[^,\s\"]+',
            rf'"{key}"\s*:\s*"[^"]*"',
            rf"'{key}'\s*:\s*'[^']*'"
        ]
        for pat in patterns:
            msg = re.sub(pat, f'{key}={self.MASK}', msg, flags=re.IGNORECASE)
        return msg

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(user)s %(request_id)s %(error_type)s %(tenant_id)s %(environment)s %(hostname)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Add context and scrub filters globally
    logger.addFilter(ContextFilter())
    logger.addFilter(ScrubFilter())

    # Optional: also log to console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger 