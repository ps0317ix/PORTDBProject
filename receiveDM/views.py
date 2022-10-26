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
from .receiveDM import receive_dm

import time
import json
import datetime
from requests_oauthlib import OAuth1Session
from google.cloud import bigquery

# 参考
# https://qiita.com/y_uehara1011/items/22c680ea0e0b13c7942b


# DM送信結果取得
class GetTwitterReceiveDMListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterReceiveDM.objects.all()
    serializer_class = TwitterReceiveDMSerializer
    log_path = "logs/test.log"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pollingTime = 70

    # DM受信
    def get_receive_dm(self, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
        twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        headers = {"content-type": "application/json"}

        url = "https://api.twitter.com/1.1/direct_messages/events/list.json"
        res = twitter.get(url, headers=headers)
        ret = json.loads(res.text)
        return ret

    # ユーザID取得
    def get_user_detail(self, user_id, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
        twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        headers = {"content-type": "application/json"}
        url = "https://api.twitter.com/1.1/users/show.json?user_id=" + user_id
        ret_json = twitter.get(url, headers=self.headers)
        return (json.loads(ret_json.text))

    def log(self, log_msg):
        log_fp = open("logs/test.log", mode="a")
        log_str = "{0:[%m/%d %H:%M.%S]} ".format(datetime.datetime.now()) + log_msg + "\n"
        print(log_str)
        log_fp.write(log_str)

    def get(self, request, format=None):
        response = []
        try:
            user = User.objects.all()
            sender_list = TwitterSender.objects.filter(user=user)

            receive_dm(sender_list)

        except Exception as e:
            print(type(e), e)
            return Response(data={'message': e}, status=status.HTTP_400_BAD_REQUEST)


class CreateTwitterReceiveDM(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterReceiveDM.objects.all()
    serializer_class = TwitterReceiveDMSerializer

    def post(self, request, format=None):
        sender_list = TwitterSender.objects.filter(user=request.user)
        response = []
        for sender in sender_list:
            dataset_id = sender.bq_dataset_id
            service_account_key = sender.GCP_account_key_upload.name
            client = bigquery.Client.from_service_account_json(service_account_key)
            table_id = "{}.{}.{}".format(client.project, dataset_id, 'send_dm')

        return Response(data={'result': response}, status=status.HTTP_200_OK)
