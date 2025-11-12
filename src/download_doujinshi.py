from __init__ import *

import threading
import time
import queue
import os
import cloudscraper


class DownloadDoujinshi:
    def __init__(self):
        self.html_info = None
        self.img_types = ['jpg', 'png', 'webp']
        self.task_list = queue.Queue()
        self.queue_lock = threading.Lock()
        self.threads = []
        self.task_num = 0
        self.task_finish = 0

    def verify_doujinshi_integrity(self):
        for page in range(int(self.html_info['page'])):
            if os.path.exists(f'{self.html_info["download_path"]}/{page + 1}.{self.html_info["img_type"]}'):
                continue
            flag = 1
            for img_type in self.img_types:
                if os.path.exists(f'{self.html_info["download_path"]}/{page + 1}.{img_type}'):
                    flag = 0
                    break
            if flag:
                self.task_list.put(page + 1)

    def print_download_info(self):
        pound_length = 30
        while self.task_finish < self.task_num:
            pound_num = int(pound_length * self.task_finish / self.task_num)
            print(f' [{"#" * pound_num}{" " * (pound_length - pound_num)}] {self.task_finish}/{self.task_num} finished\r', end='')
            time.sleep(0.1)
        print(f' [{"#" * pound_length}] {self.task_finish}/{self.task_num} finished')

    def add_download_thread(self):
        print_thread = threading.Thread(target=self.print_download_info)
        print_thread.start()

        thread_num = self.task_list.qsize()
        if thread_num > int(THREAD_NUMBER):
            thread_num = int(THREAD_NUMBER)

        for _ in range(thread_num):
            thread = threading.Thread(target=self.download_thread)
            self.threads.append(thread)
            thread.start()

        for thread in self.threads:
            thread.join()

    def download_thread(self):
        while not self.task_list.empty():
            self.queue_lock.acquire()
            work = self.task_list.get()
            self.queue_lock.release()

            request_url = f'{self.html_info["img_url"]}{work}.'
            img_type = self.html_info["img_type"]
            flag = 0
            response_html = ''

            while 1:
                try:
                    scraper_html = cloudscraper.create_scraper(browser='chrome')
                    response_html = scraper_html.get(f'{request_url}{img_type}', timeout=TIMEOUT)
                except IOError:
                    time.sleep(0.5)
                    continue
                if response_html.status_code == 200:
                    break
                if response_html.status_code == 404:
                    img_type = self.img_types[flag]
                    flag += 1
                    continue

            open(f'{self.html_info["download_path"]}/{work}.{img_type}', 'wb').write(response_html.content)
            self.task_finish += 1

    def launch(self, html_info):
        self.html_info = html_info
        self.verify_doujinshi_integrity()
        self.task_num = self.task_list.qsize()
        self.add_download_thread()


def start_download_doujinshi(html_info):
    download_doujinshi = DownloadDoujinshi()
    download_doujinshi.launch(html_info)