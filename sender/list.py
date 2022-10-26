import json
from requests_oauthlib import OAuth1Session


def get_target_list(send_type, sender, target):
    twitter = OAuth1Session(sender.CONSUMER_KEY, sender.CONSUMER_SECRET, sender.ACCESS_TOKEN,
                            sender.ACCESS_TOKEN_SECRET)
    target_users = []
    response = []
    try:
        if send_type == 'follower':
            url = "https://api.twitter.com/1.1/followers/ids.json"
            params = {
                'screen_name': target,
                'stringify_ids': True
            }
            res = twitter.get(url, params=params)
            target_users = json.loads(res.text)['ids']

        elif send_type == 'follow':
            url = "https://api.twitter.com/1.1/friends/ids.json"
            params = {
                'screen_name': target,
                'stringify_ids': True
            }
            res = twitter.get(url, params=params)
            target_users = json.loads(res.text)['ids']
        for target_user in target_users:
            obj = {
                "id": target_user,
                "url": f"https://twitter.com/i/user/{target_user}"
            }
            response.append(obj)
        return response
    except Exception as e:
        print('送信対象のフォローorフォロワーのリスト取得に失敗しました')
        print(e, type(e))
        return response
