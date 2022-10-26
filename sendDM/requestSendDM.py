import random
import string
import requests
from tenacity import retry, retry_if_exception_type, wait_exponential

from server.models import Server
from . import sendDM
from .sendDM import check_list

headers = {
    'Content-Type': 'application/json',
}


# Twitter API認証
def twitter_exe_auth(consumer_key, consumer_secret, access_token, access_secret):
    sec = 0

    base_url, basic_user, basic_password = get_server_base_url()
    url = f'{base_url}send_dm_api/v1/get_twitter_status'
    data = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_secret': access_secret
    }

    response = requests.post(url, json=data, auth=(basic_user, basic_password))
    return response


def get_target_list(send_type, worksheet, targets, target, consumer_key, consumer_secret, access_token, access_secret, screen_name):
    print(f'targets:{targets}')
    print(f'target:{target}')
    base_url, basic_user, basic_password = get_server_base_url()
    # デバック用
    # base_url = 'http://127.0.0.1:5100/'
    # url = f'{base_url}send_dm_api/v1/get_target_list'
    url = f'{base_url}send_dm_api/v2/get_target_list'

    data = {
        'send_type': send_type,
        'targets': targets,
        'target': target,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_secret': access_secret,
        'screen_name': screen_name
    }

    res = requests.post(url, json=data, auth=(basic_user, basic_password))
    response = res.json()
    errors = {}
    if res.status_code == 200:
        # 例：{'target_users': ['1245344360071233536', '1489615164618190850', '123...
        print(response)
        message = ''
        try:
            target_users = response['target_users']
        except Exception:
            raise Exception
        try:
            errors = response['errors']
        except Exception:
            pass
        return target_users, message, res.status_code, errors
    elif res.status_code == 404:
        return response['target_users'], "continue", res.status_code, response['errors']
    else:
        print('送信対象のフォローorフォロワーのリスト取得に失敗しました')
        sendDM.worksheet_delete_row(worksheet)  # リスト取得に失敗したのでスプシから削除
        raise KeyError


def get_is_spreadsheet_target_list(send_type, targets, target, consumer_key, consumer_secret, access_token, access_secret):
    try:
        print(f'targets:{targets}')
        print(f'target:@{target}')
        base_url, basic_user, basic_password = get_server_base_url()
        url = f'{base_url}send_dm_api/v1/get_target_list'
        # url = 'http://127.0.0.1:5100/send_dm_api/v1/get_target_list'

        data = {
            'send_type': send_type,
            'targets': targets,
            'target': target,
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'access_token': access_token,
            'access_secret': access_secret
        }

        response = requests.post(url, json=data, auth=(basic_user, basic_password))
        target_users = response.json()
        # 例：{'target_users': ['1245344360071233536', '1489615164618190850', '123...
        print(target_users)
        message = ''
        return target_users['target_users'], message
    except Exception as e:
        print('送信対象のフォローorフォロワーのリスト取得に失敗しました')
        print(e, type(e))
        target_users.pop(0)
        return False, e


@retry(retry=retry_if_exception_type(KeyError), wait=wait_exponential(multiplier=60*30, min=90, max=84000))
def get_target_user_detail(target_user, consumer_key, consumer_secret, access_token, access_secret):
    base_url, basic_user, basic_password = get_server_base_url()
    url = f'{base_url}send_dm_api/v1/get_target_user_detail'
    data = {
        'target_user': target_user,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_secret': access_secret,
    }
    errors = {}
    response = requests.post(url, json=data, auth=(basic_user, basic_password))
    if response.status_code == 200:
        target_user_detail = response.json()
        if 'name' in target_user_detail.keys():
            return target_user_detail, errors
        else:
            errors = target_user_detail['errors'][0]
            return target_user_detail, errors
    else:
        print('status_codeエラーによりリトライ')
        raise KeyError


@retry(retry=retry_if_exception_type(KeyError), wait=wait_exponential(multiplier=60*30, min=90, max=84000))
def get_user_detail(screen_name, consumer_key, consumer_secret, access_token, access_secret):
    base_url, basic_user, basic_password = get_server_base_url()
    url = f'{base_url}send_dm_api/v1/get_target_user_detail'
    data = {
        'username': screen_name,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_secret': access_secret
    }
    errors = {}
    response = requests.post(url, json=data, auth=(basic_user, basic_password))
    if response.status_code == 200:
        target_user_detail = response.json()
        if 'name' in target_user_detail.keys():
            return target_user_detail, errors
        else:
            errors = target_user_detail['errors'][0]
            return target_user_detail, errors
    else:
        print('status_codeエラーによりリトライ')
        print(response.json())
        raise KeyError


def post_send_dm(payload, consumer_key, consumer_secret, access_token, access_secret, screen_name):
    base_url, basic_user, basic_password = get_server_base_url()
    url = f'{base_url}send_dm_api/v1/post_send_dm'
    data = {
        'payload': payload,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_secret': access_secret,
        'screen_name': screen_name
    }

    response = requests.post(url, json=data, auth=(basic_user, basic_password))
    res = response.json()

    error_message = res['error_message']
    error_code = res['error_code']
    error_message_ja = res['error_message_ja']

    print(f'エラーメッセージ：{error_message}')
    print(f'エラーコード：{error_code}')
    print(error_message_ja)

    return error_message, error_code, error_message_ja


def random_name(n):
    rand_list = [random.choice(string.ascii_lowercase) for y in range(n)]
    return ''.join(rand_list)


def get_server_base_url():
    server_cnt = Server.objects.filter(is_active=True).count()
    print(f'稼働サーバー数：{server_cnt}')
    if server_cnt > 1:
        rand_int = random.randint(0, server_cnt - 1)
        server = Server.objects.filter(is_active=True)[rand_int]
    else:
        server = Server.objects.get(is_active=True)
    print(f'使用サーバー：{server.name}')
    return server.base_url, server.basic_user, server.basic_password 


def server_health_check_main():
    for server in Server.objects.all():
        if server.is_active:
            server_health_check(server)


def server_health_check(server):
    url = f'{server.base_url}'
    response = requests.get(url, auth=(server.basic_user, server.basic_password))
    if response.status_code == 200:
        print(f'{server.name}:{response.status_code}')
    else:
        server.is_active = False
        print(f'{server.name}を無効化')
        server.save()
