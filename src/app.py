import datetime
import json
import re
import wykop


APP_KEY = 'Ldp7XVdKMq'
SECRET_KEY = 'KIG5Phzi3r'



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
        ids = get_ids(entries)
        url = get_playlist_url(tag_name, ids)
        yield {'tag': tag_name, 'url': url}


def generate_links_json():
    api = wykop.WykopAPI(APP_KEY, SECRET_KEY)
    tags = get_tags()
    links = list(get_links(api, tags))
    return json.dumps(links)


def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")


if __name__ == '__main__':
    with open('template.html') as f:
        links = generate_links_json()
        template = f.read()
        time = get_time()
        html = template.replace("{{links}}", links).replace("{{time}}", time)

        with open('index.html', 'w') as f2:
            f2.write(html)
