import logging
import logging.handlers
import os
from pythonjsonlogger import jsonlogger

LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'agentspring.log')
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 log files

os.makedirs(LOG_DIR, exist_ok=True)

class ContextFilter(logging.Filter):
    def __init__(self, user=None, request_id=None, error_type=None):
        super().__init__()
        self.user = user
        self.request_id = request_id
        self.error_type = error_type

    def filter(self, record):
        record.user = getattr(record, 'user', self.user)
        record.request_id = getattr(record, 'request_id', self.request_id)
        record.error_type = getattr(record, 'error_type', self.error_type)
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(user)s %(request_id)s %(error_type)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Add context filter globally
    logger.addFilter(ContextFilter())

    # Optional: also log to console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger 