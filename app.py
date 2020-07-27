import datetime
from itertools import cycle
import json
import logging
import os
import re
import requests
import wykop


FIREBASE_URL = os.environ.get('FIREBASE_URL')
WYKOPAPI_KEYS = os.environ.get('WYKOPAPI_KEYS').split(',')


LOCAL = os.environ.get('LOCAL', 0)
USEFB = os.environ.get('USEFB', 1)


logging.basicConfig(filename='mirkofon.log', level=logging.DEBUG)


class WykopApiClient:

    def __init__(self, key_pairs):
        keys = [pair.split(':') for pair in key_pairs]
        self.key_iter = cycle(keys)
        self.next_api()

    def next_api(self):
        keys = self.key_iter.next()
        self.app_key = keys[0]
        self.api = wykop.WykopAPI(*keys)

    def request(self, resource, method, method_params):
        api_params = {'appkey': self.app_key}
        request_params = (resource, method, method_params, api_params)
        try:
            return self.api.request(*request_params)
        except wykop.WykopAPIError as e:
            logging.error(e)
            self.next_api()
            return self.api.request(*request_params)


def get_entries(api_client, tag_name):
    response = api_client.request('tag', 'entries', [tag_name])
    count = response['meta']['counters']['entries']
    return response['items'], count


def parse_entry(entry):
    url = entry['embed']['url']

    if 'youtube.com' in url.lower():
        return re.findall(r'\?v=(.{11})', url)[0]


def get_ids(entries):
    for entry in entries:
        try:
            video_id = parse_entry(entry)
            if video_id is not None:
                yield video_id

        except (KeyError, TypeError, IndexError):
            continue


def get_playlist_url(title, ids):
    base_url = "http://www.youtube.com/watch_videos?"
    ids = 'video_ids=' + ','.join(ids)
    title = 'title=%23' + title
    return ''.join([base_url, ids, '&', title])


def get_tags():
    with open('tags.txt') as f:
        return [l.strip() for l in f.readlines()]


def get_links(api_client, tags):
    for tag_name in tags:
        entries = get_entries(api_client, tag_name)
        ids = get_ids(entries[0])
        count = entries[1]
        url = get_playlist_url(tag_name, ids)
        yield {'tag': tag_name, 'url': url, 'count': count}


def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")


def fetch_data():
    api_client = WykopApiClient(WYKOPAPI_KEYS)

    tags = get_tags()
    links = sorted(get_links(api_client, tags), key=lambda l: l['tag'])
    time = get_time()

    data = {'meta': {'time': time},
            'items': links}
    return json.dumps(data)


if __name__ == '__main__':
    if LOCAL:
        logging.info("Reading data from file")
        with open('web/data.json') as f:
            data = f.read()
    else:
        logging.info("Fetching data from WykopAPI")
        data = fetch_data()

    if USEFB:
        logging.info("Writing to Firebase")
        url = FIREBASE_URL + 'data.json'
        response = requests.put(url, data)

    logging.info("Writing to file")
    with open('web/data.json', 'w') as json_file:
        json_file.write(data)
