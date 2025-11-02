import logging

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup and return configured logger"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)
