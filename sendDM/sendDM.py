import json
import random
import string
from datetime import datetime
from google.cloud import bigquery
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tenacity import retry, retry_if_result, wait_exponential

from .models import TwitterSendDM


def check_list(obj):
    return isinstance(obj, list)


def get_sheet_data(send_type, api_key_file, sender):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']  # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    credentials = ServiceAccountCredentials.from_json_keyfile_name(api_key_file, scope)
    gc = gspread.authorize(credentials)  # OAuth2の資格情報を使用してGoogle APIにログイン
    workbook = gc.open_by_key(sender.spread_sheet_id)
    forbidden_worksheet = workbook.worksheet('禁止リスト')
    if send_type == 'follow':
        if sender.spread_sheet_name_suffix != '':
            spread_sheet_name = f'{sender.spread_sheet_name_suffix}_フォロー送信'
        else:
            spread_sheet_name = 'フォロー送信'
        print(spread_sheet_name)
        follow_worksheet = workbook.worksheet(spread_sheet_name)
        return follow_worksheet, forbidden_worksheet
    elif send_type == 'follower':
        if sender.spread_sheet_name_suffix != '':
            spread_sheet_name = f'{sender.spread_sheet_name_suffix}_フォロワー送信'
        else:
            spread_sheet_name = 'フォロワー送信'
        print(spread_sheet_name)
        follower_worksheet = workbook.worksheet(spread_sheet_name)
        return follower_worksheet, forbidden_worksheet
    elif send_type == 'direct':
        if sender.spread_sheet_name_suffix != '':
            spread_sheet_name = f'{sender.spread_sheet_name_suffix}_直接送信'
        else:
            spread_sheet_name = '直接送信'
        print(spread_sheet_name)
        follower_worksheet = workbook.worksheet(spread_sheet_name)
        return follower_worksheet, forbidden_worksheet


# 引数の桁数だけランダムな英数字を生成
def random_name(n):
    rand_list = [random.choice(string.ascii_lowercase) for y in range(n)]
    return ''.join(rand_list)


def get_target_list(send_type, worksheet, targets, target, twitter):
    # 送信対象のフォローorフォロワーのリストを取得
    target_users = []
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

        elif send_type == 'direct':
            for i, target in enumerate(targets):
                if i == 0:
                    continue
                target_users.append(target[0])
        return target_users
    except Exception as e:
        print('送信対象のフォローorフォロワーのリスト取得に失敗しました')
        print(e, type(e))
        worksheet_delete_row(worksheet)  # リスト取得に失敗したのでスプシから削除
        return target_users


def create_bq_table(client, table_id):
    # スキーマは上で定義したものを利用
    table = bigquery.Table(table_id, schema=TwitterSendDM.schema)
    # クラスターテーブルの設定
    table.description = "Twitter DM送信ログ"
    try:
        # テーブル作成を実行
        table_res = client.create_table(table)
    except:
        pass


def get_send_dm(client, table_id, target_id):
    try:
        query = f"""
            SELECT
                COUNT(target_id) as target_id_count
            FROM
                {table_id}
            WHERE
                target_id = '{target_id}'
        """
        bq_response = client.query(query).result()

        for res in bq_response:
            target_id_count = res.target_id_count
            if target_id_count > 0:
                return True
            else:
                return False
    except Exception as e:
        print(e)
        return False


# 過去送信済リストから送信失敗したリストだけ取得
def get_sent_target_sorted_list(client, table_id, email):
    try:
        query = f"""
            SELECT
              target_id
            FROM (
              SELECT
                *,
                DENSE_RANK() OVER (PARTITION BY target_id ORDER BY updated_at DESC ) AS distinct_target_id
              FROM
                {table_id}
              WHERE
                email = '{email}'
                AND send_result != '送信済'
                )
            WHERE
              distinct_target_id = 1
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response

    except Exception as e:
        print(e)
        return False


# 過去送信済リストの取得
def get_sent_target_list(client, table_id, email):
    try:
        query = f"""
            SELECT
                target_id
            FROM
                {table_id}
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response

    except Exception as e:
        print(e)
        return False


def get_send_dm_content(client, table_id, target_id):
    try:
        query = f"""
            SELECT
                *
            FROM
                {table_id}
            WHERE
                target_id = '{target_id}'
            ORDER BY created_at DESC
            LIMIT 1
        """
        bq_response = client.query(query)
        print(len(bq_response))

        if not bq_response:
            raise Exception
        return True

    except Exception:
        return False


def get_send_dm_count(client, table_id, email, start_date, end_date):
    try:
        query = f"""
            SELECT
                COUNT(*) as count
            FROM
                {table_id}
            WHERE
                email = '{email}'
                AND created_at
                BETWEEN
                    '{start_date}'
                AND
                    '{end_date}'
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response
    except Exception as e:
        print(e)
        return 0


def get_send_dm_count_date_list(client, table_id, email, start_date, end_date):
    try:
        query = f"""
            SELECT
              CAST(created_at AS DATE) AS date,
              COUNT(CAST(created_at AS DATE)) AS count
            FROM
             (
                SELECT
                  *
                FROM
                  {table_id}
                ORDER BY created_at ASC
             )
            WHERE
              email = '{email}' AND
              created_at BETWEEN '{start_date}'
              AND '{end_date}'
            GROUP BY
              CAST(created_at AS DATE)
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response
    except Exception as e:
        print(e)
        return 0


def get_send_dm_success_count_date_list(client, table_id, email, start_date, end_date):
    try:
        query = f"""
            SELECT
              CAST(created_at AS DATE) AS date,
              COUNT(CAST(created_at AS DATE)) AS count
            FROM
             (
                SELECT
                  *
                FROM
                  {table_id}
                WHERE send_result = '送信済'
             )
            WHERE
              email = '{email}' AND
              created_at BETWEEN '{start_date}'
              AND '{end_date}'
            GROUP BY
              CAST(created_at AS DATE)
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response
    except Exception as e:
        print(e)
        return 0


def get_send_dm_success_count(client, table_id, email, start_date, end_date):
    try:
        query = f"""
            SELECT
                COUNT(*) as send_success_cnt
            FROM
                {table_id}
            WHERE
                email = '{email}'
                AND send_result = '送信済'
                AND created_at
                BETWEEN
                    '{start_date}'
                AND
                    '{end_date}'
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response
    except Exception as e:
        print(e)
        return 0


def get_send_dm_result(client, table_id, email, offset):
    try:
        query = f"""
            SELECT
                *
            FROM
                {table_id}
            WHERE
                email = '{email}'
            ORDER BY created_at DESC
            LIMIT 100
            OFFSET {offset}
        """
        bq_response = client.query(query).result()
        if not bq_response:
            raise Exception
        return bq_response
    except Exception as e:
        print(e)
        return False


def get_send_dm_by_name(client, table_id, target_name):
    try:
        query = f"""
            UPDATE
                {table_id}
            SET
                response = '返信有り',
                updated_at = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            WHERE
                target_name = '{target_name}'
        """
        bq_response = client.query(query).result()
        if bq_response.num_results > 0:
            print('DM更新')
            print(bq_response)
            return bq_response
        else:
            raise Exception
    except Exception as e:
        print(e)
        return False


def update_send_dm_by_target_id(client, table_id, target_id):
    try:
        query = f"""
            UPDATE
                {table_id}
            SET
                response = '返信有り',
                updated_at = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            WHERE
                target_id = '{target_id}'
        """
        bq_response = client.query(query).result()
        if bq_response.num_results > 0:
            print('DM更新')
            print(bq_response)
            return bq_response
        else:
            raise Exception
    except Exception as e:
        print(e)
        return False


def worksheet_delete_row(worksheet):
    worksheet.delete_row(2)
