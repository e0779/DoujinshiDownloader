import os
import sys
import configparser
import logging
import time
import cloudscraper


PATH_PROGRAM = os.path.abspath('')
PATH_CONFIG = f'{PATH_PROGRAM}/config.ini'
PATH_LOGS = f'{PATH_PROGRAM}/logs'

CURRENT_TIME = str(time.strftime("%Y-%m-%d_%H%M%S", time.localtime()))

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y/%m/%d %I:%M:%S %p'

os.makedirs(PATH_LOGS, exist_ok=True)
logging.basicConfig(filename=f'logs/{CURRENT_TIME}.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

logging.debug('Start reading config.ini')

try:
    config_file = configparser.ConfigParser()
    config_file.read(PATH_CONFIG, 'UTF-8')

    PATH_DOWNLOAD = config_file.get('main', 'DOWNLOAD_PATH')
    THREAD_NUMBER = int(config_file.get('main', 'THREAD_NUMBER'))
    RETRY_TIMES = int(config_file.get('main', 'RETRY_TIMES'))
    TIMEOUT = int(config_file.get('main', 'TIMEOUT'))
    IS_DELETE_ADS = int(config_file.get('main', 'IS_DELETE_ADS'))
except ValueError:
    logging.error('ValueError config.ini')
    print('config.ini not intact or missing.')
    input('Press Enter to exit...')
    sys.exit()
except configparser.Error:
    logging.error('configparser.Error config.ini')
    print('config.ini not intact or missing.')
    input('Press Enter to exit...')
    sys.exit()

if not PATH_DOWNLOAD:
    logging.error('PATH_DOWNLOAD missing.')
    print('Download path missing.')
    input('Press Enter to exit...')
    sys.exit()

logging.debug('End reading config')

logging.debug('Start test internet connection')

try:
    scraper = cloudscraper.create_scraper(browser='chrome')
    time_start = time.time()
    response = scraper.get('https://www.google.com/', timeout=TIMEOUT)
    time_total = time.time() - time_start
    logging.debug(f'Time total: {time_total}')
except IOError:
    logging.error('connect error')
    print('connect error')
    input('Press Enter to exit...')
    sys.exit()

logging.debug('End test internet connection')

WELCOME_TEXT = r'''
  ____               _ _           _     _   ____                      _                 _           
 |  _ \  ___  _   _ (_) |_ __  ___| |__ (_) |  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __ 
 | | | |/ _ \| | | || | | '_ \/ __| '_ \| | | | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 | |_| | (_) | |_| || | | | | \__ \ | | | | | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
 |____/ \___/ \__,_|/ |_|_| |_|___/_| |_|_| |____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   
                  |__/ Code by Odyzzey 2025 in python3.11.8 UTF-8

 [+]Get comics from hanime1.me / nhentai.net
 [+]Pls install Tampermonkey with kidC to use this program more conveniently
'''

print(WELCOME_TEXT)