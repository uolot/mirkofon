import re
import wykop


APP_KEY = 'Ldp7XVdKMq'
SECRET_KEY = 'KIG5Phzi3r'
URL_PREFIX = "http://www.youtube.com/watch_videos?video_ids="


api = wykop.WykopAPI(APP_KEY, SECRET_KEY)


def get_entries(api, tag_name):
    response = api.request('tag', 'entries', [tag_name], {'appkey': APP_KEY})
    return response['items']


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


def get_playlist_url(ids):
    return URL_PREFIX + ','.join(ids)


def get_tags():
    with open('tags.txt') as f:
        return [l.strip() for l in f.readlines()]


if __name__ == '__main__':
    for tag_name in get_tags():
        entries = get_entries(api, tag_name)
        ids = get_ids(entries)
        print tag_name, get_playlist_url(ids)
