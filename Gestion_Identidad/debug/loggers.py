import os
import logging
from datetime import datetime

# Define ruta raíz de logs
BASE_LOG_DIR = os.path.join(os.path.dirname(__file__), 'historico')
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Fecha actual para nombrar archivos
today_str = datetime.now().strftime('%Y%m%d')

# Función para crear loggers
def create_logger(logger_name, file_prefix):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        log_file_path = os.path.join(BASE_LOG_DIR, f"{file_prefix}_{today_str}.log")
        handler = logging.FileHandler(log_file_path, encoding='utf-8', mode='a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Loggers disponibles
instagram_logger = create_logger("instagram", "Instagram")
general_logger = create_logger("general", "General")
google_logger = create_logger("google", "Google")
twitter_logger = create_logger("twitter", "Twitter")
linkedin_logger = create_logger("linkedin", "linkedin")
