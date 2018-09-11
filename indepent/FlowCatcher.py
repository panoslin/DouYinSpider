import json
import redis
import requests
import os
import uuid
import time

if not os.path.exists('Download'):
    os.makedirs('Download')
r = redis.Redis(host='10.16.4.216', port=6379, db=8)


def response(flow):
    url = 'aweme/v1/feed/'
    if url in flow.request.url:
        text = flow.response.text
        data = json.loads(text)['aweme_list']
        for aweme in data:
            if aweme['is_ads']:
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
                with open('Download/{video_name}.mp4'.format(video_name=res['uid']), 'wb') as video:
                    video.write(requests.get(res['video_url']).content)
                print(json.dumps(res, sort_keys=True, indent='\n'))
                while True:
                    try:
                        res['size']=os.path.getsize('Download/{video_name}.mp4'.format(video_name=res['uid']))
                        break
                    except Exception:
                        continue
                r.hset('ame:data:Ver1', res['aweme_id'], res)
