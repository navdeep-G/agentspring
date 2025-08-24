def audit_log(action: str, user: str = "unknown", details: dict = None):
    import logging

    logger = logging.getLogger()
    logger.info(
        f"AUDIT: {action}", extra={"user": user, "details": details or {}}
    )
