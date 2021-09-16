import difflib as dl
import logging
from re import I
from hugo_to_dev_to import convert_hugo_article_to_dev_to, split_preamble_and_content
from typing import Any, Dict, List, Tuple

from dev_to import Client as DevToClient
from hugo import Client as HugoClient

import pprint

CONTENT_DIR = 'content/posts'

logging.basicConfig(level=logging.INFO)

pprint = pprint.PrettyPrinter().pprint

def dict_diffs(a: Dict[str, Any], b: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    added_to_b_dict: Dict[str, Any] = {k: b[k] for k in set(b) - set(a)}
    removed_from_a_dict: Dict[str, Any] = {k: a[k] for k in set(a) - set(b)}
    common_dict_a: Dict[str, Any] = {k: a[k] for k in set(a) & set(b) if a[k] != b[k]}
    common_dict_b: Dict[str, Any] = {k: b[k] for k in set(a) & set(b) if b[k] != a[k]}
    return added_to_b_dict, removed_from_a_dict, common_dict_a, common_dict_b

def articles_are_identical(hugo_article, dev_to_article):
    preamble_comparison = dict_diffs(hugo_article['preamble'], dev_to_article['preamble'])
    diffs = sum([len(d) for d in preamble_comparison])
    if diffs != 0:
        logging.info(f"Preambles do not match: {preamble_comparison}")
        return False
    if hugo_article['content'].strip() != dev_to_article['content'].strip():
        logging.info(f"Content does not match.")
        # diffs = dl.ndiff(hugo_article['content'].splitlines(keepends=True),
        #     dev_to_article['content'].splitlines(keepends=True)
        # )
        # print(''.join(diffs), end="")
        return False
    return True

def main():
    devToClient = DevToClient()
    hugoClient = HugoClient(CONTENT_DIR)
    dev_to_articles = devToClient.get_articles()
    hugo_articles = hugoClient.get_articles()

    article_crossref = []
    for hugo_article in hugo_articles:
        matching_articles = [a for a in dev_to_articles if a.title == hugo_article['title']]
        article = hugo_article
        if len(matching_articles) > 0:
            article['dev.to'] = matching_articles[0]
        else:
            article['dev.to'] = None
        article_crossref.append(article)

    logging.info(f"Found {len(hugo_articles)} hugo articles.")

    for article in article_crossref:
        if article['hugo'] is not None:
            article['filename'] = article['hugo']['filename']
            if article['dev.to'] is None:
                article['action'] = 'upload'
                article['dev.to'] = convert_hugo_article_to_dev_to(article['hugo'])
            else:
                article['action'] = 'compare'
                article['id'] = article['dev.to'].id
                article['dev.to'] = split_preamble_and_content(article['dev.to'].body_markdown)
        else:
            article['action'] = 'none'

    new_articles = [a for a in article_crossref if a['action'] == 'upload']
    
    logging.info(f"Found {len(new_articles)} articles which are not on Dev.to.")

    for article in new_articles:
        print(f"Uploading '{article['title']}'...", end='')
        try:
            devToClient.publish_article(article['dev.to'])
        except IOError as err:
            article['result'] = 'failure'
            article['error'] = err
            logging.error(err)
            print("failed.")
        else:
            article['result'] = 'success'
            article['error'] = None
            print("done.")

    compare_articles = [a for a in article_crossref if a['action'] == 'compare']

    for article in compare_articles:
        article['generated_content'] = convert_hugo_article_to_dev_to(article['hugo'])
        if articles_are_identical(article['generated_content'], article['dev.to']):
            article['action'] = 'no action'
        else:
            article['action'] = 'update'

    update_articles = [a for a in article_crossref if a['action'] == 'update']

    logging.info(f"Found {len(update_articles)} articles which need to be updated.")

    for article in update_articles:
        print(f"Updating '{article['title']}...'")
        try:
            devToClient.update_article(article['id'], article['generated_content'])
        except IOError as err:
            article['result'] = 'failure'
            article['error'] = err
            logging.error(err)
            logging.error(err.response.text)
            print("failed.")
        else:
            article['result'] = 'success'
            article['error'] = None
            print("done.")


if __name__ == '__main__':
    main()