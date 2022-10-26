from django.http import HttpResponse, Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import TwitterSendDMSerializer
from sender.models import TwitterSender
from sendContent.models import TwitterSendContent
from .models import TwitterSendDM
from user.models import User
import receiveDM.receiveDM as receiveDM
from . import sendDM, requestSendDM, zendesk

import time
import json
import random
import datetime
import slackweb
from datetime import timedelta
from google.cloud import bigquery
from requests_oauthlib import OAuth1Session

slack = slackweb.Slack(url="https://hooks.slack.com/services/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")


class GetTwitterSendListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):
        date_list = []
        res_date_list = []
        send_dm_cnt_list = []
        send_dm_success_cnt_list = []
        try:
            start_date = datetime.datetime.today() - timedelta(days=request.data['duration'])  # 開始日
            end_date = datetime.datetime.today() + timedelta(days=1)  # 終了日
            startDate = start_date.strftime('%Y-%m-%d')
            endDate = end_date.strftime('%Y-%m-%d')
            sender_list = TwitterSender.objects.filter(user=request.user)
            send_dm_cnt = 0
            send_dm_success_cnt = 0

            try:
                sender = sender_list[0]
                if len(TwitterSendContent.objects.filter(user=request.user)) == 0:
                    raise Exception
            except Exception:
                start_date = datetime.datetime.today() - timedelta(days=7)  # 開始日
                end_date = datetime.datetime.today() + timedelta(days=1)  # 終了日
                days_num = (end_date - start_date).days + 1
                date_list = map(lambda x, y=start_date: y + timedelta(days=x), range(days_num))
                for d in date_list:
                    res_date_list.append(d.strftime('%Y/%m/%d'))
                    send_dm_cnt_list.append(0)
                    send_dm_success_cnt_list.append(0)
                return Response(data={'date_list': res_date_list, 'send_dm_cnt_list': send_dm_cnt_list,
                                      'send_dm_success_cnt_list': send_dm_success_cnt_list}, status=status.HTTP_200_OK)

            dataset_id = 'send_dm'
            service_account_key = 'GCP_account_keys/port-v2-service-account-key.json'
            client = bigquery.Client.from_service_account_json(service_account_key)
            table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

            results = sendDM.get_send_dm_count_date_list(client, table_id, request.user.email, startDate, endDate)
            success_results = sendDM.get_send_dm_success_count_date_list(client, table_id, request.user.email,
                                                                         startDate, endDate)
            results_list = []
            success_results_list = []
            for result in results:
                obj = {
                    "date": result.date.strftime('%Y/%m/%d'),
                    "send_dm_cnt": result.count
                }
                results_list.append(obj)
            for success_result in success_results:
                obj = {
                    "date": success_result.date.strftime('%Y/%m/%d'),
                    "send_dm_success_cnt": success_result.count,
                }
                success_results_list.append(obj)

            response = sorted(results_list, key=lambda x: x['date'])
            success_response = sorted(success_results_list, key=lambda x: x['date'])
            date_list = []
            send_dm_cnt_list = []
            send_dm_success_cnt_list = []
            for res in response:
                date_list.append(res['date'])
                send_dm_cnt_list.append(res['send_dm_cnt'])
                search = list(filter(lambda item: item['date'] == res['date'], success_response))
                try:
                    send_dm_success_cnt_list.append(search[0]['send_dm_success_cnt'])
                except IndexError:
                    send_dm_success_cnt_list.append(0)
            return Response(data={'date_list': date_list, 'send_dm_cnt_list': send_dm_cnt_list,
                                  'send_dm_success_cnt_list': send_dm_success_cnt_list}, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            start_date = datetime.datetime.today() - timedelta(days=7)  # 開始日
            end_date = datetime.datetime.today()  # 終了日
            days_num = (end_date - start_date).days + 1
            date_list = map(lambda x, y=start_date: y + timedelta(days=x), range(days_num))
            for d in date_list:
                res_date_list.append(d.strftime('%Y/%m/%d'))
                send_dm_cnt_list.append(0)
                send_dm_success_cnt_list.append(0)
            return Response(data={'date_list': res_date_list, 'send_dm_cnt_list': send_dm_cnt_list,
                                  'send_dm_success_cnt_list': send_dm_success_cnt_list}, status=status.HTTP_200_OK)


# Twitter DM送信中か判定(GET)
class IsTwitterSendExe(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def get(self, request, format=None):
        try:
            sender_list = TwitterSender.objects.filter(user=request.user)
            res_list = []
            for sender in sender_list:
                last_send_dm = TwitterSendDM.objects.filter(sender_screen_name=sender.screen_name).order_by(
                    '-created_at').first()
                if last_send_dm:
                    td = datetime.timedelta(minutes=2)
                    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
                    res_list.append((datetime.datetime.now(JST) - last_send_dm.created_at) > td)
                for res in res_list:
                    if not res:
                        return Response(data={'is_send_exe': True}, status=status.HTTP_200_OK)  # 送信中
            return Response(data={'is_send_exe': False}, status=status.HTTP_200_OK)  # 直近の送信なし
            # return Response(data={'is_send_exe': None}, status=status.HTTP_200_OK)  # 送信履歴なし
        except TwitterSender.DoesNotExist:
            raise Http404


# Twitter DM送信中か判定(POST)
class ClientIsTwitterSendExe(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):
        try:
            try:
                user = User.objects.get(uuid=request.data['data']['uuid'])
            except Exception:
                user = request.user
            sender_list = TwitterSender.objects.filter(user=user)

            res_list = []
            for sender in sender_list:
                last_send_dm = TwitterSendDM.objects.filter(sender_screen_name=sender.screen_name).order_by(
                    '-created_at').first()
                if last_send_dm:
                    td = datetime.timedelta(minutes=2)
                    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
                    res_list.append((datetime.datetime.now(JST) - last_send_dm.created_at) > td)
                for res in res_list:
                    if not res:
                        return Response(data={'is_send_exe': True}, status=status.HTTP_200_OK)  # 送信中
            return Response(data={'is_send_exe': False}, status=status.HTTP_200_OK)  # 直近の送信なし

        except TwitterSender.DoesNotExist:
            raise Http404


# Twitter DM送信数取得(POST)
class GetTwitterSendDMCnt(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):
        try:
            sender_list = TwitterSender.objects.filter(user=request.user)
            res_list = []
            send_cnt = 0
            send_success_cnt = 0
            for sender in sender_list:
                dataset_id = 'send_dm'
                service_account_key = 'GCP_account_keys/port-v2-service-account-key.json'
                client = bigquery.Client.from_service_account_json(service_account_key)
                table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

                start_date = datetime.datetime.today() - timedelta(days=request.data['duration'])  # 開始日
                end_date = datetime.datetime.today()  # 終了日
                startDate = start_date.strftime('%Y-%m-%d')
                endDate = end_date.strftime('%Y-%m-%d')

                result = sendDM.get_send_dm_count(client, table_id, request.user.email, startDate, endDate)
                for res in result:
                    send_cnt = send_cnt + res.count

                result = sendDM.get_send_dm_success_count(client, table_id, request.user.email, startDate, endDate)
                for res in result:
                    send_success_cnt = send_success_cnt + res.send_success_cnt

            return Response(data={'sendCnt': send_cnt, 'sendSuccessCnt': send_success_cnt},
                            status=status.HTTP_200_OK)  # 直近の送信なし

        except TwitterSender.DoesNotExist:
            raise Http404


# DM送信実行のmaster機能View(POST)
class TwitterSendDMMaster(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):

        targets = []
        response = {}
        res_error = ''
        account_cnt = 0  # 送信アカウント数
        send_type = request.data['data']['type']
        try:
            is_spread_sheet = request.data['data']['isSpreadSheet']
        except KeyError:
            is_spread_sheet = True
        try:
            target_users = request.data['data']['sendTarget']
        except KeyError:
            target_users = []
        try:
            forbidden_targets = request.data['data']['forbiddenTarget']
        except KeyError:
            forbidden_targets = []
        try:
            user = User.objects.get(uuid=request.data['data']['uuid'])
        except Exception:
            user = request.user

        print('送信リストへのDM送信を開始します')
        loop_max = 1
        loop_cnt = 0

        forbidden_words = ['エロ', '右翼', '左翼', 'SHIP!!', 'SHIP']

        # サーバーヘルスチェック
        # requestSendDM.server_health_check_main()

        # 無限ループ
        while loop_max >= loop_cnt:
            try:
                # 送信アカウントインデックス
                sleep_time = random.randint(90, 100)  # 遅延時間
                time_sta = sleep_time
                sender_index = 0
                j = 0
                x = 0
                send_cnt = 0
                send_comp_cnt = 0

                try:
                    sender_list = TwitterSender.objects.filter(sender_id=request.data['data']['senderId'])
                except Exception:
                    sender_list = TwitterSender.objects.filter(user=user, is_active=True)

                sender_list_for_log = sender_list
                sender = {}
                get_target_sender = {}
                max_sender_count = len(sender_list)
                if sender_index == 0:
                    time_sta = time.perf_counter()

                if len(sender_list) > 0:
                    try:
                        sender = sender_list[sender_index]  # 送信アカウント選択
                        get_target_sender = sender_list[random.randrange(len(sender_list))]
                        print(f'ランダムでAPI使用ユーザー選定：{get_target_sender.screen_name}')
                    except Exception as e:
                        print(e)
                        return Response(data={'message': e}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    print('DM送信を終了します')
                    return Response(data={'message': 'DM送信を終了します'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    if send_cnt == 0:
                        print('スクリーン名を最新のものに更新')
                        for s in sender_list:
                            updateScreenName(s.sender_id, s.CONSUMER_KEY, s.CONSUMER_SECRET, s.ACCESS_TOKEN,
                                             s.ACCESS_TOKEN_SECRET)
                except Exception as e:
                    print(e)

                GCP_account_key_upload = 'media/' + sender.GCP_account_key_upload.name
                spread_sheet_id = ''
                worksheet = {}
                forbidden_sheet = {}

                if is_spread_sheet:
                    # 送信タイプによってスプシのシートを切り替える
                    spread_sheet_id = sender.spread_sheet_id
                    worksheet, forbidden_sheet = sendDM.get_sheet_data(send_type, GCP_account_key_upload, sender)

                    targets = worksheet.get_all_values()
                    forbidden_targets = forbidden_sheet.get_all_values()
                    loop_max = len(targets) - 1

                    if len(targets) <= 1:
                        res_error = '送信対象を入力してください。'
                        raise ValueError(res_error)

                    target = targets[1][0]
                    target = target.replace('@', '')

                    if target == '送信対象':
                        continue  # ヘッダーをスキップ
                    elif target == '':
                        print('送信終了')
                        break  # 送信対象がなくなったら終了

                    # oauthlibのインスタンス生成
                    rand_int = random.randint(0, len(sender_list) - 1)
                    target_users, message, status_code, errors = requestSendDM.get_target_list(send_type, worksheet,
                                                                                               targets, target,
                                                                                               sender_list[
                                                                                                   rand_int].CONSUMER_KEY,
                                                                                               sender_list[
                                                                                                   rand_int].CONSUMER_SECRET,
                                                                                               sender_list[
                                                                                                   rand_int].ACCESS_TOKEN,
                                                                                               sender_list[
                                                                                                   rand_int].ACCESS_TOKEN_SECRET,
                                                                                               sender_list[
                                                                                                   rand_int].screen_name)
                    worksheet.delete_row(2)
                    if errors != {}:
                        print(f'{str(sleep_time)}min遅延')
                        time.sleep(sleep_time / 2)
                        print(f'残り{str(sleep_time / 2)}秒')
                        time.sleep(sleep_time / 2)
                        continue

                else:
                    if send_type == 'direct':
                        target_users = target_users.split('\n')
                    else:
                        target = target_users[0]
                        target = target.replace('@', '')
                        target_users = requestSendDM.get_is_spreadsheet_target_list(send_type, targets, target,
                                                                                    get_target_sender.CONSUMER_KEY,
                                                                                    get_target_sender.CONSUMER_SECRET,
                                                                                    get_target_sender.ACCESS_TOKEN,
                                                                                    get_target_sender.ACCESS_TOKEN_SECRET)

                # 過去送信DMターゲットとの重複削除
                if send_type != 'direct':
                    print('重複削除開始')
                    for sender in sender_list:
                        dataset_id = sender.bq_dataset_id
                        service_account_key = 'media/GCP_account_keys/port-v2-service-account-key.json'
                        client = bigquery.Client.from_service_account_json(service_account_key)

                        table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

                        # sendDM.create_bq_table(client, table_id)

                        sent_targets = sendDM.get_sent_target_list(client, table_id, user.email)
                        for sent_target in sent_targets:
                            try:
                                target_users.remove(sent_target.target_id)
                            except ValueError:
                                continue

                if not target_users:
                    print('target_usersがないため戻ります')
                    worksheet.delete_row(2)  # スプシから削除
                    continue

                if len(target_users) < 5:
                    print(f'もうすぐ{sender.screen_name}の送信が完了します。')

                # 送信文取得
                send_contents = TwitterSendContent.objects.filter(user=user)  # 送信内容取得
                send_contents_cnt = len(send_contents)

                sender_cnt = len(sender_list)
                target_user_cnt = len(target_users)
                print(f'送信アカウント名：{sender.screen_name}')
                print(f'送信アカウント数：{str(sender_cnt)}')
                print(f'送信対象アカウント数：{str(target_user_cnt)}')

                contents = []
                success = 0
                error_codes = []
                error_users_list = []
                send_request_cnt = 0
                is_sender_pop = False

                for j, target_user in enumerate(target_users):
                    try:
                        is_forbidden = False

                        for forbidden_target in forbidden_targets:
                            if target_user == forbidden_target[0]:
                                is_forbidden = True

                        if is_forbidden:
                            print(f'{target_user}は禁止リストに含まれるためスキップ')
                            if type == 'direct':
                                if is_spread_sheet:
                                    worksheet.delete_row(2)
                                else:
                                    target_users.pop(0)
                            continue

                        print('-------------------------------------')
                        print(f'{sender_index + 1}番目のアカウントで送信します')

                        if send_type == 'direct':
                            if is_spread_sheet:
                                worksheet.delete_row(2)
                            else:
                                target_users.pop(0)
                            if len(target_users) - 5 == j:
                                print(f'もうすぐ{target}の送信が完了します。')

                        elif len(target_users) == j:
                            print(f'送信リクエスト数：{str(j)}')
                            print(f'送信成功数：{str(send_comp_cnt)}')
                            print(f'送信完了率：{str(round((send_comp_cnt / send_cnt) * 100))}%')
                            raise ValueError('登録アカウントが存在しないため処理を終了します')

                        account_cnt += 1
                        sender = ''
                        CONSUMER_KEY = ''
                        CONSUMER_SECRET = ''
                        ACCESS_TOKEN = ''
                        ACCESS_TOKEN_SECRET = ''

                        try:
                            sender = sender_list[sender_index]

                            CONSUMER_KEY = sender.CONSUMER_KEY
                            CONSUMER_SECRET = sender.CONSUMER_SECRET
                            ACCESS_TOKEN = sender.ACCESS_TOKEN
                            ACCESS_TOKEN_SECRET = sender.ACCESS_TOKEN_SECRET

                        except Exception as e:
                            print(e)
                            success = 0
                            for z, error in enumerate(error_codes):
                                try:
                                    print(f'{str(z + 1)}:@{sender_list_for_log[z].screen_name}のエラーコード：{error}')
                                except Exception as e:
                                    print(e)

                            error_codes.clear()
                            sender_index = 0
                            print(f'{str(sleep_time)}min遅延')
                            time.sleep(sleep_time / 2)
                            print(f'残り{str(sleep_time / 2)}秒')
                            time.sleep(sleep_time / 2)  # 84秒間隔が上限？

                        # 送信対象チェック
                        try:
                            data, errors = requestSendDM.get_target_user_detail(target_user,
                                                                                get_target_sender.CONSUMER_KEY,
                                                                                get_target_sender.CONSUMER_SECRET,
                                                                                get_target_sender.ACCESS_TOKEN,
                                                                                get_target_sender.ACCESS_TOKEN_SECRET)
                            if errors != {}:
                                j += 1
                                print(f'{str(sleep_time)}min遅延')
                                time.sleep(sleep_time / 2)
                                print(f'残り{str(sleep_time / 2)}秒')
                                time.sleep(sleep_time / 2)
                                continue
                            print('ターゲット情報')
                            target_name = data['name']
                            target_id = data['id']
                            try:
                                target_screen_name = data['screen_name']
                            except KeyError:
                                target_screen_name = data['username']
                            try:
                                target_description = data['description']
                            except Exception:
                                target_description = ''
                            try:
                                target_follow_count = data['public_metrics']['following_count']
                            except Exception:
                                target_follow_count = 0
                            try:
                                target_followers_count = data['public_metrics']['followers_count']
                            except Exception:
                                target_followers_count = 0

                        except ValueError as e:
                            print(e)
                            j += 1
                            continue
                        except Exception as e:
                            print(e)
                            print('error-code')
                            error_code = str(e.args[0][0]['code'])
                            print(error_code)
                            if error_code == "50" or error_code == "34":
                                print("送信先ユーザーが存在しません")
                                j += 1
                                continue
                            if error_code == "63":
                                print("送信先ユーザーが凍結されている可能性があります")
                                j += 1
                                continue
                            print(f"@{sender.screen_name}を送信アカウントから一時外します")
                            pop_sender = TwitterSender.objects.get(sender_id=sender.sender_id)
                            pop_sender.is_active = False
                            pop_sender.save()
                            return Response(data={
                                'message': 'Twitter DM送信完了',
                            }, status=status.HTTP_200_OK)

                        if x == send_contents_cnt:
                            x = 0
                        send_message = send_contents[x].content

                        # パラメーター用ランダム変数
                        rand = sendDM.random_name(6)
                        message_text = send_message.format(rand, target_name)

                        print(datetime.datetime.now())
                        print(f'送信先ID：{str(target_id)}')
                        print(f'送信先：{str(target_name)}')

                        dataset_id = 'send_dm'
                        service_account_key = 'media/GCP_account_keys/port-v2-service-account-key.json'
                        client = bigquery.Client.from_service_account_json(service_account_key)
                        table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

                        send_res = sendDM.get_send_dm(client, table_id, target_id)

                        # 送信履歴を検索し、履歴がある場合はスキップ
                        if send_res and send_type != 'direct' and is_spread_sheet == False:
                            print('送信済なのでスキップ')
                            continue

                        for forbidden_word in forbidden_words:
                            if forbidden_word in target_description:
                                print(f'禁止ワード{forbidden_word}を含むのでスキップ')
                                continue

                        if target_followers_count > 100000:
                            continue

                        res = ''

                        try:
                            # 送信実行とDB格納
                            print(f'送信主:@{sender.screen_name}')

                            res = ''
                            error_code = '200'
                            error_message = ''
                            error_message_ja = ''
                            try:
                                payload = {"event":
                                               {"type": "message_create",
                                                "message_create": {
                                                    "target": {"recipient_id": target_id},
                                                    "message_data": {"text": message_text, }
                                                }
                                                }
                                           }
                                payload = json.dumps(payload)

                                if sender_index == max_sender_count:
                                    time_end = time.perf_counter()
                                    tim = time_end - time_sta
                                    if sleep_time < tim:
                                        sleep_time = 10
                                error_message, error_code, error_message_ja = requestSendDM.post_send_dm(payload,
                                                                                                         CONSUMER_KEY,
                                                                                                         CONSUMER_SECRET,
                                                                                                         ACCESS_TOKEN,
                                                                                                         ACCESS_TOKEN_SECRET,
                                                                                                         sender.screen_name)

                                send_result = ''
                                try:
                                    if error_code == '200':
                                        send_result = '送信済'
                                    else:
                                        send_result = '送信失敗'

                                    print(f'対象：{target_id}')

                                    TwitterSendDM.objects.create(
                                        sender_screen_name=sender.screen_name,
                                        target_id=target_id,
                                        target_name=target_name,
                                        target_screen_name=target_screen_name,
                                        target_description=target_description,
                                        target_follow_count=target_follow_count,
                                        target_followers_count=target_followers_count,
                                        content="",
                                        send_result=send_result,
                                        response=''
                                    )

                                except Exception as e:
                                    print(f'送信文データDB挿入エラー：{e}')
                                try:
                                    rows_to_insert = [{
                                        "sender_screen_name": sender.screen_name,
                                        "email": user.email,
                                        "target_id": target_id,
                                        "target_name": target_name,
                                        "target_screen_name": target_screen_name,
                                        "target_description": target_description,
                                        "target_follow_count": target_follow_count,
                                        "target_followers_count": target_followers_count,
                                        "content": message_text,
                                        "send_result": send_result,
                                        "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }]

                                    errors = client.insert_rows_json(table_id, rows_to_insert,
                                                                     row_ids=[None] * len(rows_to_insert))
                                    if len(errors) > 0:
                                        raise Exception

                                except Exception as e:
                                    print(f'送信文データBQ挿入エラー：{e}')

                            except Exception as e:
                                print('DM送信実行に失敗しました')
                                print(e)

                            x += 1

                            error_codes.append(error_code)
                            if error_code == '200' or error_code == '349' or error_code == '150' or error_code == '108':
                                pass
                            else:
                                raise ValueError(error_message)

                        except Exception as e:
                            print(type(e), e)
                            if 'automated' in str(e):
                                break
                            print(f'@{sender.screen_name}を送信アカウントから一時外します')
                            slack.notify(
                                text=f'<@U02CTN73EUV> <@U034YK356MT>\n@{sender.screen_name}で送信エラー発生しました。認証などを確認してください。\nエラ：{type(e), e}')
                            # sender_list.pop(sender_index)
                            pop_sender = TwitterSender.objects.get(sender_id=sender.sender_id)
                            pop_sender.is_active = False
                            pop_sender.save()
                            sender_cnt = len(sender_list) - 1
                            is_sender_pop = True
                            break

                        send_cnt += 1
                        print('送信完了数：' + str(send_cnt))

                        if error_code == '200' or error_code == '349':
                            contents.append(target_id)
                            contents.append('送信済')
                            if error_code == '200':
                                send_comp_cnt += 1

                            print(f'送信対象数：{str(target_user_cnt)}')
                            print(f'送信リクエスト数：{str(j)}')
                            remain_target_cnt = target_user_cnt - j
                            print(f'送信残数：{str(remain_target_cnt)}')
                            print(f'送信成功数：{str(send_comp_cnt)}')
                            print(f'送信完了率：{str(round((send_comp_cnt / send_cnt) * 100))}%')

                            # DM返信履歴取得
                            # receiveDM.receive_dm(sender_list)

                            if remain_target_cnt == 1 and send_type == 'direct':
                                return Response(data={
                                    'message': 'Twitter DM送信完了',
                                }, status=status.HTTP_200_OK)
                            elif sender_index + 1 == sender_cnt:
                                print('１つ目のアカウントに戻ります')
                                sender_index = 0
                                for z, error in enumerate(error_codes):
                                    try:
                                        print(f'{str(z + 1)}:@{sender_list_for_log[z].screen_name}のエラーコード：{error}')
                                    except Exception as e:
                                        print(e)

                                error_codes.clear()
                                for error_user in error_users_list:
                                    print(f'ロボット認証が必要なアカウント：{error_user}')
                                print(f'最終遅延：{str(sleep_time)}min')
                                time.sleep(sleep_time / 2)
                                print(f'残り{str(sleep_time / 2)}秒')
                                time.sleep(sleep_time / 2)
                            else:
                                print('次のアカウントで送信します')
                                success += 1
                                sender_index += 1
                        else:
                            print(f'送信対象数：{str(target_user_cnt)}')
                            print(f'送信リクエスト数：{str(j)}')
                            remain_target_cnt = target_user_cnt - j
                            print(f'送信残数：{str(remain_target_cnt)}')
                            print(f'送信成功数：{str(send_comp_cnt)}')
                            print(f'送信完了率：{str(round((send_comp_cnt / send_cnt) * 100))}%')

                            contents.append(target_id)
                            contents.append('送信失敗')

                            if remain_target_cnt == 1 and send_type == 'direct':
                                return Response(data={
                                    'message': 'Twitter DM送信完了',
                                }, status=status.HTTP_200_OK)
                            elif sender_index + 1 == sender_cnt:
                                print('１つ目のアカウントに戻ります')
                                sender_index = 0
                                if success > 0:
                                    success = 0
                                    for z, error in enumerate(error_codes):
                                        try:
                                            print(f'{str(z + 1)}:@{sender_list_for_log[z].screen_name}のエラーコード：{error}')
                                        except Exception as e:
                                            print(e)

                                    error_codes.clear()

                                    for error_user in error_users_list:
                                        print(f'ロボット認証が必要なアカウント：{error_user}')

                                    print(str(sleep_time) + 'min遅延')
                                    time.sleep(sleep_time / 2)
                                    print(f'残り{str(sleep_time / 2)}秒')
                                    time.sleep(sleep_time / 2)
                                else:
                                    print(str(sleep_time) + 'min遅延')
                                    time.sleep(sleep_time / 2)
                                    print(f'残り{str(sleep_time / 2)}秒')
                                    time.sleep(sleep_time / 2)

                            else:
                                print('次のアカウントで送信します')
                                sender_index += 1
                                if target_user_cnt == send_cnt:
                                    break
                    except Exception as e:
                        res_error = str(e)
                        print(e)
                        break

                if is_sender_pop:
                    continue
                try:
                    if is_spread_sheet:
                        worksheet, forbidden_worksheet = sendDM.get_sheet_data(send_type, GCP_account_key_upload,
                                                                               sender)
                        remain_target_length = 0
                        try:
                            remain_target_length = len(worksheet.get_all_values())
                        except AttributeError as e:
                            print(e, type(e))
                            worksheet.delete_row(2)  # 送信完了したのでスプシから削除
                            loop_cnt += 1
                        if remain_target_length > 1:
                            worksheet.delete_row(2)  # 送信完了したのでスプシから削除
                            loop_cnt += 1
                        else:
                            return Response(data={
                                'message': 'Twitter DM送信完了',
                            }, status=status.HTTP_200_OK)
                    else:
                        remain_target_length = len(target_users)
                        if remain_target_length > 1:
                            target_users.pop(0)
                            loop_cnt += 1
                        else:
                            return Response(data={
                                'message': 'Twitter DM送信完了',
                            }, status=status.HTTP_200_OK)
                except Exception as e:
                    print('送信処理中にエラー発生')
                    print(e, type(e))
                    return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e, type(e))
                return Response(data={'message': res_error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={
            'message': 'Twitter DM送信完了',
        }, status=status.HTTP_200_OK)


# DM送信結果取得
class GetTwitterSendResultListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):
        sender_list = TwitterSender.objects.filter(user=request.user)
        response = []
        for sender in sender_list:
            dataset_id = 'send_dm'
            service_account_key = 'GCP_account_keys/port-v2-service-account-key.json'
            client = bigquery.Client.from_service_account_json(service_account_key)
            table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

            result = sendDM.get_send_dm_result(client, table_id, request.user.email, request.data['offset'])
            for res in result:
                response.append(res)

        return Response(data={'response': response}, status=status.HTTP_200_OK)


# DM送信結果取得
class GetTwitterListResultListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def post(self, request, format=None):
        # 送信タイプによってスプシのシートを切り替える
        sender = TwitterSender.objects.get(pk=request.data['pk'])
        GCP_account_key_upload = 'media/' + sender.GCP_account_key_upload.name
        spread_sheet_id = sender.spread_sheet_id
        list_worksheet = sendDM.get_list_worksheet(GCP_account_key_upload, spread_sheet_id)


# DM送信結果取得
class TwitterSendResultUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendDM.objects.all()
    serializer_class = TwitterSendDMSerializer

    def put(self, request, format=None):
        # 送信タイプによってスプシのシートを切り替える
        sender_list = TwitterSender.objects.filter(is_zendesk=True)
        for sender in sender_list:
            dataset_id = 'send_dm'
            service_account_key = 'GCP_account_keys/port-v2-service-account-key.json'
            client = bigquery.Client.from_service_account_json(service_account_key)
            table_id = "{}.{}.{}".format('superb-leaf-313807', dataset_id, 'send_dm')

            zendesk_email = sender.zendesk_email
            zendesk_subdomain = sender.zendesk_subdomain
            zendesk_api_key = sender.zendesk_api_key
            response_users = zendesk.get_zendesk_ticket(zendesk_email, zendesk_subdomain, zendesk_api_key)

            for user in response_users:
                user_name = user['name']
                try:
                    send_dm = TwitterSendDM.objects.get(target_name=user_name)
                    send_dm.response = '返信有り'
                    send_dm.save()

                    sendDM.get_send_dm_by_name(client, table_id, user_name)
                except Exception as e:
                    print(e, type(e))

        return Response(data={'message': '更新完了'}, status=status.HTTP_200_OK)


def updateScreenName(sender_id, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    screen_name = ''
    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    url = f"https://api.twitter.com/2/users/{sender_id}"
    res = twitter.get(url)
    try:
        twitter_res = json.loads(res.text)['data']
        sender = TwitterSender.objects.get(sender_id=sender_id)
        sender.screen_name = twitter_res['username']
        sender.save()
        return sender
    except KeyError as e:
        print(e)
        return e
