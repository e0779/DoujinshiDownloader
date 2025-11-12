from __init__ import *

import logging
import cloudscraper
from bs4 import BeautifulSoup
import time
import queue
import os


def string_standard(trans: str) -> str:
    return trans.translate(str.maketrans('', '', '\\/:*?"<>|'))

def string_line_break(trans) -> str:
    return trans.get_text()[3:].strip().translate(str.maketrans('\n', ','))


class DoujinshiInfo:
    def __init__(self):
        self.html_info = {'parody': 'None', 'characters': 'None', 'tags': 'None', 'artists': 'None',
                          'group': 'None', 'language': 'None', 'category': 'None', 'page': 'None',
                          'source_url': 'None'}
        self.url = ''
        self.html = None

    def write_info(self):
        if not os.path.isdir(self.html_info["download_path"]):
            os.makedirs(self.html_info["download_path"])
        if not os.path.exists(f'{self.html_info["download_path"]}/info.txt'):
            with open(f'{self.html_info["download_path"]}/info.txt', 'a', encoding='utf-8') as f:
                f.write(f'original name: {self.html_info["original_name"]}\n')
                f.write(f'translated name: {self.html_info["translated_name"]}\n')
                f.write(f'artists: {self.html_info["artists"]}\n')
                f.write(f'group: {self.html_info["group"]}\n')
                f.write(f'characters: {self.html_info["characters"]}\n')
                f.write(f'tags: {self.html_info["tags"]}\n')
                f.write(f'language: {self.html_info["language"]}\n')
                f.write(f'parody: {self.html_info["parody"]}\n')
                f.write(f'category: {self.html_info["category"]}\n')
                f.write(f'page: {self.html_info["page"]}\n')
                f.write(f'source url: {self.html_info["source_url"]}\n')
                f.write(f'img url: {self.html_info["img_url"]}')

    def print_info(self):
        os.system('cls')
        print('original_name:', self.html_info['original_name'])
        print('translated_name', self.html_info['translated_name'])
        print('artists', self.html_info['artists'])
        print('group', self.html_info['group'])
        print('characters', self.html_info['characters'])
        print('tags', self.html_info['tags'])
        print('page', self.html_info['page'])
        print('\n')

    def get_download_info(self, url: str):
        self.url = url
        self.get_url_html()
        if not self.get_url_html():
            logging.error(f'Failed to get html')
            return None
        logging.debug(f'success get html info')
        self.analyze_html()
        self.write_info()
        self.print_info()
        return self.html_info

    def get_url_html(self):
        try_times = 3
        while try_times:
            try:
                logging.debug(f'Trying {try_times} times getting html')
                scraper_html = cloudscraper.create_scraper(browser='chrome')
                response_html = scraper_html.get(self.url, timeout=3)
                self.html = BeautifulSoup(response_html.text, 'lxml')
                logging.debug(f'successfully got html')
                return True
            except IOError:
                logging.error(f'Trying {try_times} times getting html failed')
                try_times -= 1
                time.sleep(0.5)
        return None

    def analyze_html(self):
        self.html_info['source_url'] = self.url

        if not self.url.find('anime') == -1:
            self.html_info['doujinshi_id'] = string_standard(f'01{self.url[self.url.find("comic") + 6:]}')
            cover_url = str(self.html.find(style='border-radius: 5px; width: 100%;')['data-src'])
            self.html_info['img_url'] = cover_url[0:cover_url.find('cover')].replace('t2', 'i2')
            self.html_info['img_type'] = cover_url[cover_url.find('cover') + 6:]
            title = self.html.find_all(class_='pretty')
            self.html_info['translated_name'] = title[0].text
            self.html_info['original_name'] = title[1].text

            for i in self.html.find_all(style='margin:0; color: #d9d9d9;'):
                if not i.get_text().find('同人') == -1:
                    self.html_info['parody'] = string_line_break(i)
                elif not i.get_text().find('角色') == -1:
                    self.html_info['characters'] = string_line_break(i)
                elif not i.get_text().find('標籤') == -1:
                    self.html_info['tags'] = string_line_break(i)
                elif not i.get_text().find('作者') == -1:
                    self.html_info['artists'] = string_line_break(i)
                elif not i.get_text().find('社團') == -1:
                    self.html_info['group'] = string_line_break(i)
                elif not i.get_text().find('語言') == -1:
                    self.html_info['language'] = string_line_break(i)
                elif not i.get_text().find('分類') == -1:
                    self.html_info['category'] = string_line_break(i)
                elif not i.get_text().find('頁數') == -1:
                    self.html_info['page'] = string_line_break(i)

        if not self.url.find('hentai') == -1:
            self.html_info['doujinshi_id'] = string_standard(f'02{self.url[self.url.find("/g/") + 3:]}')
            cover_url = str(self.html.find(itemprop="image")['content'])
            self.html_info['img_url'] = f'i1{cover_url[4:cover_url.find("cover")]}'
            self.html_info['img_type'] = cover_url[cover_url.find('cover') + 6:]
            title = self.html.find_all(class_='pretty')
            self.html_info['translated_name'] = title[0].text
            self.html_info['original_name'] = title[1].text

            tags_name = queue.Queue()
            tags_num = queue.Queue()
            tags_exist = queue.Queue()

            tags = str(self.html.find(id="tags").get_text())

            if not tags.find('Parodies') == -1:
                tags_exist.put('parody')
            if not tags.find('Characters') == -1:
                tags_exist.put('characters')
            if not tags.find('Tags') == -1:
                tags_exist.put('tags')
            if not tags.find('Artists') == -1:
                tags_exist.put('artists')
            if not tags.find('Groups') == -1:
                tags_exist.put('group')
            if not tags.find('Languages') == -1:
                tags_exist.put('language')
            if not tags.find('Categories') == -1:
                tags_exist.put('category')
            if not tags.find('Pages') == -1:
                tags_exist.put('page')

            for i in self.html.find_all('span', class_='tags'):
                tags_num.put(str(i).count('class="name"'))

            for i in self.html.find_all('span', class_='name'):
                tags_name.put(str(i.get_text()))

            while not tags_num.empty():
                num = tags_num.get()
                if num == 0:
                    if tags_exist.empty():
                        break
                    self.html_info[tags_exist.get()] = 'None'
                    continue
                text = ''
                for i in range(num - 1):
                    text += f'{tags_name.get()} '
                text += tags_name.get()
                self.html_info[tags_exist.get()] = text

        if not self.html_info['artists'] == 'None':
            name_artists = self.html_info['artists']
        elif not self.html_info['group'] == 'None':
            name_artists = self.html_info['group']
        else:
            name_artists = 'Anonymous'
        if not name_artists.find(',') == -1:
            name_artists = 'Anthology'
        name_artists = string_standard(name_artists)
        name_title = string_standard(self.html_info['translated_name'])
        self.html_info['download_folder'] = f'[{name_artists}] {name_title}'
        self.html_info['download_path'] = f'{PATH_DOWNLOAD}/{self.html_info["download_folder"]}'


def get_html_info(url: str):
    doujinshi_info = DoujinshiInfo()
    return doujinshi_info.get_download_info(url)
