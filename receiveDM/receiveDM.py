from django.http import Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import TwitterReceiveDMSerializer
from sender.models import TwitterSender
from sendDM.models import TwitterSendDM
from user.models import User
from sendDM import sendDM
from .models import TwitterReceiveDM

import time
import json
import datetime
from requests_oauthlib import OAuth1Session
from google.cloud import bigquery

# 参考
# https://qiita.com/y_uehara1011/items/22c680ea0e0b13c7942b


# DM受信
def get_receive_dm(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    headers = {"content-type": "application/json"}

    url = "https://api.twitter.com/1.1/direct_messages/events/list.json"
    res = twitter.get(url, headers=headers)
    ret = json.loads(res.text)
    return ret


# ユーザID取得
def get_user_detail(user_id, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    headers = {"content-type": "application/json"}
    url = "https://api.twitter.com/1.1/users/show.json?user_id=" + user_id
    headers = {"content-type": "application/json"}
    ret_json = twitter.get(url, headers=headers)
    return json.loads(ret_json.text)


def log(log_msg):
    log_fp = open("logs/test.log", mode="a")
    log_str = "{0:[%m/%d %H:%M.%S]} ".format(datetime.datetime.now()) + log_msg + "\n"
    print(log_str)
    log_fp.write(log_str)


# DM返信結果取得
def receive_dm(sender_list):
    response = []
    try:
        for sender in sender_list:
            try:
                print('-------------------------')
                print(f'{sender.screen_name}の返信取得中')
                print('-------------------------')
                CONSUMER_KEY = sender.CONSUMER_KEY
                CONSUMER_SECRET = sender.CONSUMER_SECRET
                ACCESS_TOKEN = sender.ACCESS_TOKEN
                ACCESS_TOKEN_SECRET = sender.ACCESS_TOKEN_SECRET
            except Exception as e:
                print(f'{sender.screen_name}の返信取得中にエラー発生')
                print(type(e), e)
                continue

            ret = get_receive_dm(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            try:
                messages = ret["events"]
            except Exception as e:
                print(type(e), e)
                continue

            for m in messages:
                # 送信者のスクリーンネームを取得
                user_detail = get_user_detail(m["message_create"]["sender_id"], CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                receive_dm_sender_name = user_detail["screen_name"]
                receive_dm_sender_id = user_detail["id_str"]
                # 本文取得
                msg_text = m["message_create"]["message_data"]["text"]

                # 自分自身の発言は除外
                if receive_dm_sender_name != sender.screen_name:
                    TwitterReceiveDM.objects.get_or_create(
                        sender=sender,
                        msg_text=msg_text,
                        receive_dm_sender_id=receive_dm_sender_id,
                        receive_dm_sender_name=receive_dm_sender_name
                    )

                    try:
                        send_dm = TwitterSendDM.objects.get(target_id=receive_dm_sender_id)
                        send_dm.response = '返信有り'
                        send_dm.save()

                        dataset_id = sender.bq_dataset_id
                        service_account_key = sender.GCP_account_key_upload.name
                        client = bigquery.Client.from_service_account_json(service_account_key)
                        table_id = "{}.{}.{}".format(client.project, dataset_id, 'send_dm')

                        sendDM.update_send_dm_by_target_id(client, table_id, receive_dm_sender_id)
                    except Exception as e:
                        print(type(e), e)
                        pass

    except Exception as e:
        print(type(e), e)

