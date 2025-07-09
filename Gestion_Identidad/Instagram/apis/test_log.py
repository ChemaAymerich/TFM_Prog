# test_log.py
import logging
import os
import datetime

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), 'historico_debug')
    os.makedirs(log_dir, exist_ok=True)
    today_str = datetime.datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'Debug_{today_str}.log')
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

setup_logging()
logging.debug("🚀 Log de prueba funcionando.")
