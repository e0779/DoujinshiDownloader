from __init__ import *
from get_html_info import get_html_info
from download_doujinshi import start_download_doujinshi

import threading
import pyperclip
import queue
import time

class DoujinshiDownloader:
    def __init__(self):
        self.download_queue = queue.Queue()
        self.url = ''

    def clipboard_monitor(self):
        approval_url_list = [
            lambda: recent_paste.find('hanime1.me/comic/') != -1,
            lambda: recent_paste.find('nhentai.net/g/') != -1
        ]
        previous_paste = ''
        while True:
            recent_paste = pyperclip.paste()
            if previous_paste == recent_paste:
                continue
            if not any(rule() for rule in approval_url_list):
                continue

            logging.debug(f'Clipboard detected {recent_paste}')
            previous_paste = recent_paste
            self.download_queue.put(recent_paste)

            time.sleep(0.1)

    def start_clipboard_monitor(self):
        logging.debug('Starting clipboard monitor')
        clipboard_monitor_thread = threading.Thread(target=self.clipboard_monitor)
        clipboard_monitor_thread.start()

    def get_download_queue(self):
        while True:
            if self.download_queue.empty():
                continue
            self.url = self.download_queue.get()
            print(self.url)
            #self.start_doujinshi_download()
            time.sleep(0.1)

    def start_get_download_queue(self):
        get_download_queue_thread = threading.Thread(target=self.get_download_queue)
        get_download_queue_thread.start()

    def start_doujinshi_download(self):
        logging.debug(f'start doujinshi download')
        time_total_start = time.perf_counter()
        logging.debug(f'start get html info')
        html_info = get_html_info(self.url)
        if not html_info:
            logging.error('Download info failed.')
            return
        start_download_doujinshi(html_info)
        time_total_end = time.perf_counter()
        logging.debug(f'Ending download, took {round(time_total_end - time_total_start, 2)}s\n')

    def launch(self):
        self.start_clipboard_monitor()
        self.start_get_download_queue()


if __name__ == '__main__':
    From = DoujinshiDownloader()
    From.launch()