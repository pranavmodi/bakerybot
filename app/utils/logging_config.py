import logging

def setup_logging() -> logging.Logger:
    """Configure and return the logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__) 