from os import listdir
from os.path import isfile, join
from typing import Dict, List
from hugo_to_dev_to import split_preamble_and_content

class Client:
    def __init__(self, hugo_dir: str):
        self._hugo_dir = hugo_dir

    @staticmethod
    def _get_article(filename):
        with open(filename) as file:
            content = file.read()

        content = split_preamble_and_content(content)
        content['filename'] = filename
        content['title'] = content['preamble']['title']
        return content

    def get_articles(self) -> List[Dict[str,str]]:
        files = [f for f in listdir(self._hugo_dir) if isfile(join(self._hugo_dir, f))]
        retval = []
        for file in files:
            article = {}
            article['filename'] = self._hugo_dir + '/' + file
            article['hugo'] = self._get_article(article['filename'])
            article['title'] = article['hugo']['title']
            retval.append(article)
        return retval