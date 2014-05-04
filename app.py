import datetime
import json
import os
import re
import wykop


APP_KEY = os.environ.get('MIRKO_KEY')
SECRET_KEY = os.environ.get('MIRKO_SECRET')


def get_entries(api, tag_name):
    response = api.request('tag', 'entries', [tag_name], {'appkey': APP_KEY})
    count = response['meta']['counters']['entries']
    return response['items'], count


def parse_entry(entry):
    url = entry['embed']['url']

    if 'youtube.com' in url.lower():
        video_id = re.findall(r'\?v=(.{11})', url)[0]
        return video_id


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


def get_links(api, tags):
    for tag_name in tags:
        entries = get_entries(api, tag_name)
        ids = get_ids(entries[0])
        count = entries[1]
        url = get_playlist_url(tag_name, ids)
        yield {'tag': tag_name, 'url': url, 'count': count}


def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")


def generate_response_json():
    api = wykop.WykopAPI(APP_KEY, SECRET_KEY)

    tags = get_tags()
    links = sorted(get_links(api, tags), key=lambda l: l['tag'])
    time = get_time()

    data = {'meta': {'time': time},
            'items': links}
    return json.dumps(data)


if __name__ == '__main__':
    data = generate_response_json()

    with open('web/data.json', 'w') as json_file:
        json_file.write(data)
