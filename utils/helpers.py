import logging

logging.basicConfig(level=logging.INFO)

def log_step(message: str):
    logging.info(message)


cache = {}

def get_cache(key):
    return cache.get(key)

def set_cache(key, value):
    cache[key] = value