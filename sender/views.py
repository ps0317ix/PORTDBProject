import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from sendDM.requestSendDM import twitter_exe_auth
from requests_oauthlib import OAuth1Session

from django.http import HttpResponse, Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import TwitterSenderSerializer
from .models import TwitterSender
from .list import get_target_list
from user.models import User
from sendDM.models import TwitterSendDM
from sendDM import requestSendDM


# TwitterDM送信アカウント情報取得のView(GET)
class TwitterSenderListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSender.objects.all()
    serializer_class = TwitterSenderSerializer

    def get(self, request, format=None):
        try:
            sender_list = TwitterSender.objects.all()
            response = []
            for sender in sender_list:
                last_send_dm = TwitterSendDM.objects.filter(sender_screen_name=sender.screen_name).order_by('created_at').last()
                if last_send_dm:
                    td = datetime.timedelta(minutes=2)
                    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
                    try:
                        is_sending_dm = (datetime.datetime.now(JST) - last_send_dm.created_at) > td
                    except Exception:
                        is_sending_dm = True
                else:
                    is_sending_dm = True


                obj = {
                    'id': sender.id,
                    'screen_name': sender.screen_name,
                    'password': sender.password,
                    'sender_id': sender.sender_id,
                    'CONSUMER_KEY': sender.CONSUMER_KEY,
                    'CONSUMER_SECRET': sender.CONSUMER_SECRET,
                    'ACCESS_TOKEN': sender.ACCESS_TOKEN,
                    'ACCESS_TOKEN_SECRET': sender.ACCESS_TOKEN_SECRET,
                    'spread_sheet_id': sender.spread_sheet_id,
                    'spread_sheet_name_suffix': sender.spread_sheet_name_suffix,
                    'gcp_api_key': sender.gcp_api_key,
                    'GCP_account_key_upload': sender.GCP_account_key_upload.name.replace('GCP_account_keys/', ''),
                    'bq_project_id': sender.bq_project_id,
                    'bq_dataset_id': sender.bq_dataset_id,
                    'is_zendesk': sender.is_zendesk,
                    'zendesk_email': sender.zendesk_email,
                    'zendesk_subdomain': sender.zendesk_subdomain,
                    'zendesk_api_key': sender.zendesk_api_key,
                    'is_active': sender.is_active,
                    'is_sending_dm': is_sending_dm
                }
                response.append(obj)
            return Response(data={'response': response}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        try:
            user = User.objects.get(uuid=request.data['data'])
            sender_list = TwitterSender.objects.filter(user=user)
            response = []
            for sender in sender_list:
                obj = {
                    'id': sender.id,
                    'screen_name': sender.screen_name,
                    'password': sender.password,
                    'sender_id': sender.sender_id,
                    'CONSUMER_KEY': sender.CONSUMER_KEY,
                    'CONSUMER_SECRET': sender.CONSUMER_SECRET,
                    'ACCESS_TOKEN': sender.ACCESS_TOKEN,
                    'ACCESS_TOKEN_SECRET': sender.ACCESS_TOKEN_SECRET,
                    'spread_sheet_id': sender.spread_sheet_id,
                    'spread_sheet_name_suffix': sender.spread_sheet_name_suffix,
                    'gcp_api_key': sender.gcp_api_key,
                    'GCP_account_key_upload': sender.GCP_account_key_upload.name.replace('GCP_account_keys/', ''),
                    'bq_project_id': sender.bq_project_id,
                    'bq_dataset_id': sender.bq_dataset_id,
                    'zendesk_email': sender.zendesk_email,
                    'zendesk_subdomain': sender.zendesk_subdomain,
                    'zendesk_api_key': sender.zendesk_api_key,
                    'is_active': sender.is_active
                }
                response.append(obj)
            return Response(data={'response': response}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404


# TwitterDM送信アカウント情報取得のView(GET)
class TwitterSenderHealthCheckListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSender.objects.all()
    serializer_class = TwitterSenderSerializer

    def get(self, request, format=None):
        try:
            sender_list = TwitterSender.objects.filter(user=request.user)
            response = []
            for sender in sender_list:
                res = twitter_exe_auth(sender.CONSUMER_KEY, sender.CONSUMER_SECRET, sender.ACCESS_TOKEN, sender.ACCESS_TOKEN_SECRET)
                obj = {
                    'screen_name': sender.screen_name,
                    'password': sender.password,
                    'sender_id': sender.sender_id,
                    'status': res.status_code
                }
                response.append(obj)
            return Response(data={'response': response}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        try:
            user = User.objects.get(uuid=request.data['data'])
            sender_list = TwitterSender.objects.filter(user=user)
            response = []
            for sender in sender_list:
                res = twitter_exe_auth(sender.CONSUMER_KEY, sender.CONSUMER_SECRET, sender.ACCESS_TOKEN, sender.ACCESS_TOKEN_SECRET)
                obj = {
                    'screen_name': sender.screen_name,
                    'password': sender.password,
                    'sender_id': sender.sender_id,
                    'status': res.status_code
                }
                response.append(obj)
            return Response(data={'response': response}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404


# TwitterDM送信アカウント情報登録のView(POST)
class TwitterSenderRegister(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSender.objects.all()
    serializer_class = TwitterSenderSerializer

    def post(self, request, format=None):
        try:
            try:
                if len(request.data['sender']['uuid']) > 0:
                    user = User.objects.get(uuid=request.data['sender']['uuid'])
            except KeyError as e:
                user = User.objects.get(email=request.user.email)

            username = request.data['sender']['screen_name'].replace('@', '')
            CONSUMER_KEY = request.data['sender']['CONSUMER_KEY']
            CONSUMER_SECRET = request.data['sender']['CONSUMER_SECRET']
            ACCESS_TOKEN = request.data['sender']['ACCESS_TOKEN']
            ACCESS_TOKEN_SECRET = request.data['sender']['ACCESS_TOKEN_SECRET']

            try:
                password = request.data['sender']['password']
            except KeyError:
                return Response(data={'message': 'パスワードがありません'}, status=status.HTTP_400_BAD_REQUEST)

            # oauthlibのインスタンス生成
            twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            url = f"https://api.twitter.com/2/users/by/username/{username}"
            res = twitter.get(url)
            try:
                twitter_res = json.loads(res.text)['data']
                # twitter_res, errors = requestSendDM.get_target_user_detail(username, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            except KeyError as e:
                print(e)
                print('Twitter APIかスクリーン名が間違っています。正しいAPIキーを入力してください。')
                return Response(data={
                    'message': 'Twitter APIかスクリーン名が間違っています。正しいAPIキーを入力してください。',
                }, status=status.HTTP_401_UNAUTHORIZED)

            if res.status_code == 401:
                return Response(data={
                    'message': 'Twitter APIが認証されていません。正しいAPIキーを入力してください。',
                }, status=status.HTTP_401_UNAUTHORIZED)

            screen_name = twitter_res['username']
            sender_id = twitter_res['id']

            is_zendesk = False
            zendesk_email = ""
            zendesk_subdomain = ""
            zendesk_api_key = ""
            spread_sheet_name_suffix = ""

            try:
                spread_sheet_name_suffix = request.data['sender']['spread_sheet_name_suffix']
            except KeyError:
                pass

            try:
                is_zendesk = request.data['sender']['is_zendesk']
                zendesk_email = request.data['sender']['zendesk_email']
                zendesk_subdomain = request.data['sender']['zendesk_subdomain']
                zendesk_api_key = request.data['sender']['zendesk_api_key']
            except KeyError:
                pass

            if is_zendesk:
                twitterSender = TwitterSender.objects.create(
                    sender_id=sender_id,
                    screen_name=screen_name,
                    password=password,
                    spread_sheet_id=request.data['sender']['spread_sheet_id'],
                    spread_sheet_name_suffix=spread_sheet_name_suffix,
                    CONSUMER_KEY=CONSUMER_KEY,
                    CONSUMER_SECRET=CONSUMER_SECRET,
                    ACCESS_TOKEN=ACCESS_TOKEN,
                    ACCESS_TOKEN_SECRET=ACCESS_TOKEN_SECRET,
                    bq_project_id=request.data['sender']['bq_project_id'],
                    bq_dataset_id=request.data['sender']['bq_dataset_id'],
                    is_zendesk=is_zendesk,
                    zendesk_email=zendesk_email,
                    zendesk_subdomain=zendesk_subdomain,
                    zendesk_api_key=zendesk_api_key,
                )
            else:
                twitterSender = TwitterSender.objects.create(
                    sender_id=sender_id,
                    screen_name=screen_name,
                    password=password,
                    spread_sheet_id=request.data['sender']['spread_sheet_id'],
                    spread_sheet_name_suffix=spread_sheet_name_suffix,
                    CONSUMER_KEY=CONSUMER_KEY,
                    CONSUMER_SECRET=CONSUMER_SECRET,
                    ACCESS_TOKEN=ACCESS_TOKEN,
                    ACCESS_TOKEN_SECRET=ACCESS_TOKEN_SECRET,
                    bq_project_id=request.data['sender']['bq_project_id'],
                    bq_dataset_id=request.data['sender']['bq_dataset_id'],
                    is_zendesk=is_zendesk
                )

            twitterSender.user.add(user)

            return Response(data={
                'message': 'ユーザー作成成功',
                'sender_id': sender_id
            }, status=status.HTTP_201_CREATED)
        except TwitterSender.DoesNotExist:
            raise Http404


# TwitterDM送信アカウント更新のView(PUT)
class TwitterSenderUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TwitterSenderSerializer
    queryset = User.objects.all()

    def put(self, request, format=None):
        try:
            instance = User.objects.get(email=request.user.email)
            twitterSender = TwitterSender.objects.get(screen_name=request.data['sender']['screen_name'])
            twitterSender.screen_name = request.data['sender']['screen_name']
            twitterSender.password = request.data['sender']['password']
            twitterSender.spread_sheet_id = request.data['sender']['spread_sheet_id']
            twitterSender.spread_sheet_name_suffix = request.data['sender']['spread_sheet_name_suffix']
            twitterSender.CONSUMER_KEY = request.data['sender']['CONSUMER_KEY']
            twitterSender.CONSUMER_SECRET = request.data['sender']['CONSUMER_SECRET']
            twitterSender.ACCESS_TOKEN = request.data['sender']['ACCESS_TOKEN']
            twitterSender.ACCESS_TOKEN_SECRET = request.data['sender']['ACCESS_TOKEN_SECRET']
            twitterSender.gcp_api_key = request.data['sender']['gcp_api_key']
            twitterSender.bq_project_id = request.data['sender']['bq_project_id']
            twitterSender.bq_dataset_id = request.data['sender']['bq_dataset_id']
            twitterSender.is_active = request.data['sender']['is_active']

            try:
                twitterSender.is_zendesk = request.data['sender']['is_zendesk']
                if request.data['sender']['is_zendesk']:
                    twitterSender.zendesk_email = request.data['sender']['zendesk_email']
                    twitterSender.zendesk_subdomain = request.data['sender']['zendesk_subdomain']
                    twitterSender.zendesk_api_key = request.data['sender']['zendesk_api_key']
            except KeyError:
                pass

            twitterSender.save()
            return Response(data={'message': 'ユーザー更新完了',}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise Http404


# TwitterDM送信アカウント削除のView(DELETE)
class TwitterSenderDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TwitterSenderSerializer
    queryset = TwitterSender.objects.all()

    def delete(self, request, format=None):
        try:
            twitterSender = TwitterSender.objects.get(sender_id=request.data['sender']['sender_id'])
            twitterSender.delete()
            return Response(data={
                'message': 'Twitterアカウント情報削除完了',
            }, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404


# 指定アカウントのリスト取得のView(GET)
class TwitterGetListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSender.objects.all()
    serializer_class = TwitterSenderSerializer

    def post(self, request, format=None):
        try:
            sender_list = TwitterSender.objects.filter(user=request.user)
            response = []
            sender = sender_list[0]
            response = get_target_list(request.data['payload']['type'], sender, request.data['payload']['target'])

            GCP_account_key_upload = sender.GCP_account_key_upload.name
            spread_sheet_id = sender.spread_sheet_id
            wb = get_workbook(GCP_account_key_upload, spread_sheet_id)
            list_worksheet = wb.add_worksheet(title=f"リスト取得_{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}", rows='100', cols='2')

            ds = list_worksheet.range(f'A1:A{len(response)}')
            for index, cell in enumerate(ds):
                twitter_id = response[index]['id']
                cell.value = twitter_id
            list_worksheet.update_cells(ds)

            ds = list_worksheet.range(f'B1:B{len(response)}')
            for index, cell in enumerate(ds):
                cell.value = response[index]['url']
            list_worksheet.update_cells(ds)

            return Response(data={'response': response, 'spread_sheet_id': spread_sheet_id}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404


# アカウントキーの保存
class TwitterSenderKeyRegister(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        key_file = request.data['file']
        key_name = key_file.name
        sender_id = request.data['sender_id']

        sender = TwitterSender.objects.get(sender_id=sender_id)
        sender.GCP_account_key_upload = key_file
        sender.gcp_api_key = key_name
        sender.save()
        return Response(data=[], status=status.HTTP_201_CREATED)


def get_workbook(api_key_file, spread_sheet_id):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']  # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    credentials = ServiceAccountCredentials.from_json_keyfile_name(api_key_file, scope)
    gc = gspread.authorize(credentials)  # OAuth2の資格情報を使用してGoogle APIにログイン
    workbook = gc.open_by_key(spread_sheet_id)
    return workbook
