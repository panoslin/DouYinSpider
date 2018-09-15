import json
import redis
import requests
import os
import uuid
import configparser

# Download videos to the dirctory 'Download'
PathDownload = 'Download'
if not os.path.exists(PathDownload):
    os.makedirs(PathDownload)
# Connection to redis db
config = configparser.ConfigParser()
config.read("Redis.ini")
host = config.get("redis", "host")
port = config.getint("redis", "port")
db = config.getint("redis", "db")
r = redis.Redis(host=host, port=port, db=db)


def response(flow):
    # capture request that return next 6 videos info
    url = 'aweme/v1/feed/'
    if url in flow.request.url:
        text = flow.response.text
        data = json.loads(text)['aweme_list']
        for aweme in data:
            if aweme['is_ads']: # identify whether if the current video is commercial
                # determine whether if the video exists
                if not r.hexists("ame:data:Ver1", aweme['aweme_id']):
                    res = dict()
                    res['is_ads'] = aweme['is_ads']
                    res['avatar_url'] = aweme['author']['avatar_larger']['url_list'][0]
                    res['register_time'] = aweme['author']['create_time']
                    res['authorname'] = aweme['author']['nickname']
                    res['author_user_id'] = aweme['author_user_id']
                    res['aweme_id'] = aweme['aweme_id']
                    res['broadcast_time'] = aweme['create_time']
                    res['desc'] = aweme['desc']
                    res['duration'] = int(str(aweme['duration'])[:-3])
                    res['comment_count'] = aweme['statistics']['comment_count']
                    res['digg_count'] = aweme['statistics']['digg_count']
                    res['forward_count'] = aweme['statistics']['forward_count']
                    res['play_count'] = aweme['statistics']['play_count']
                    res['share_count'] = aweme['statistics']['share_count']
                    res['video_url'] = aweme['video']['play_addr']['url_list'][0]
                    res['height'] = aweme['video']['height']
                    res['width'] = aweme['video']['width']
                    res['uid'] = str(uuid.uuid1())
                    # Download the video
                    with open('Download/{video_name}.mp4'.format(video_name=res['uid']), 'wb') as video:
                        video.write(requests.get(res['video_url']).content)
                    while True:# Get the size of the video when it is downloaded completely
                        try:
                            res['size'] = os.path.getsize('Download/{video_name}.mp4'.format(video_name=res['uid']))
                            break
                        except Exception:
                            continue
                    # Insert the data into redis database
                    r.hset('ame:data:Ver1', res['aweme_id'], res)
