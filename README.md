参考教材：https://www.udemy.com/course/python-django-web/

### サーバー起動(ポート 5001)
```bash
ngrok http --region=us --hostname=master-server.ngrok.io 5001
```

### マイグレーションファイル作成
python manage.py makemigrations アプリケーション名 --name マイグレーション名
```bash
$ python manage.py makemigrations app --name add_project
```

### マイグレーション実行
python manage.py migrate アプリケーション名
```bash
$ python manage.py migrate app
```

### マイグレーションリストの表示
```bash
$ python manage.py showmigrations
```

### マイグレーションしてない状態に戻る
```bash
$ python manage.py migrate アプリケーション名 zero
```

### スーパーユーザー作成
```bash
$ python manage.py createsuperuser
```

### DB復元参考
https://beecoder.org/ja/django/how-to-migrate-data-from-sqlite-to-postgresql-in-django-in-django


### CRUD機能
参考：https://qiita.com/xKxAxKx/items/60e8fb93d6bbeebcf065


## デプロイ方法
masterにマージした時に.github/workflows/cd-workflow.ymlを元に、Github Actionsでcdが走ってAWSにデプロイされます


# 本番環境構築
## CloudFormation
参考：https://zenn.dev/soshimiyamoto/articles/d9d425ded03ac5
deploymentファイルはこちら：
https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/kubernetes_engine/django_tutorial/polls.yaml

gcloudコマンドで構築するプロジェクトのあるアカウントでログイン
```bash
gcloud auth application-default login
```

Cloud SQL Auth Proxy をダウンロード
```bash
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.arm64
```

Cloud SQL Auth Proxy を動作可能に
```bash
chmod +x cloud_sql_proxy
```

Cloud SQL Auth Proxy を有効化
```bash
./cloud_sql_proxy -instances="superb-leaf-313807:asia-northeast1:port-project"=tcp:5432
```

PostgresSQL インスタンスを作成
```bash
gcloud sql instances create port-project \
    --project superb-leaf-313807 \
    --database-version POSTGRES_13 \
    --tier db-f1-micro \
    --region asia-northeast1
```

DB作成
```bash
gcloud sql databases create port \
    --instance port-project
```

ユーザー作成
```bash
gcloud sql users create konome \
    --instance port-project \
    --password konomekonomekonome007
```
環境変数に登録
```bash
export DATABASE_NAME=port
export DATABASE_USER=konome
export DATABASE_PASSWORD=konomekonomekonome007
```

クラスター構築
オートスケール対応
```bash
gcloud container clusters create port-backend-server \
  --scopes "https://www.googleapis.com/auth/userinfo.email","cloud-platform" \
  --zone "asia-northeast1-a" \
  --enable-autoscaling --max-nodes=32 --min-nodes=16
```

オートスケール非対応
```bash
gcloud container clusters create port-backend-server \
  --scopes "https://www.googleapis.com/auth/userinfo.email","cloud-platform" \
  --zone "asia-northeast1-a" \
  --num-nodes 16
```

kubectlとGKEクラスタを接続
```bash
gcloud container clusters get-credentials port-backend-server --zone "asia-northeast1-a"
```

シークレット作成
```bash
kubectl create secret generic cloudsql-oauth-credentials \
  --from-file=credentials.json=media/GCP_account_keys/port-v2-service-account-key.json
  ```
```bash
kubectl create secret generic cloudsql \
  --from-literal=database=port \
  --from-literal=username=konome \
  --from-literal=password=konomekonomekonome007
```

Cloud SQL プロキシのパブリック Docker イメージを取得
```bash
docker pull b.gcr.io/cloudsql-docker/gce-proxy
```

Docker イメージをビルド
```bash
docker build -t gcr.io/superb-leaf-313807/port-backend-server .
```

認証ヘルパーとして gcloud を使用するように Docker を構成し、イメージを Container Registry に push
```bash
gcloud auth configure-docker
```
```bash
docker push gcr.io/superb-leaf-313807/port-backend-server
```

GKE リソースを作成
```bash
kubectl apply -f kubernetes/managed-cert.yml
```
```bash
kubectl apply -f kubernetes/deployment.yaml
```
```bash
kubectl apply -f kubernetes/managed-cert-ingress.yml
```

デバック
```bash
kubectl get pods
```
```bash
kubectl logs [YOUR_POD_ID]
```

異常なpodがないかチェック
```bash
kubectl get pods --all-namespaces | grep -v Running
```

サーバー状態を表示
```bash
kubectl describe node
```

IPアドレス確認
```bash
kubectl get services port-backend-server
```

静的IP作成
```bash
gcloud compute addresses create port-backend-server-ip --global
```

GKE リソースを削除
```bash
kubectl delete -f kubernetes/managed-cert.yml
```
```bash
kubectl delete -f kubernetes/deployment.yaml
```
```bash
kubectl delete -f kubernetes/managed-cert-ingress.yml
```

# DBバックアップ
DBバックアップ機能参考資料
https://djangobrothers.com/blogs/djang_dbbackup/
DUMPファイルを使用してSQLite3からPostgresSQLに移行：
https://beecoder.org/ja/django/how-to-migrate-data-from-sqlite-to-postgresql-in-django-in-django
```bash
python manage.py dbbackup 
```

リストアする時
```bash
python manage.py dbrestore
```

パスを通さないとエラーが出ます
Mac
```bash
export GOOGLE_APPLICATION_CREDENTIALS=media/GCP_account_keys/port-v2-service-account-key.json
```
Windows
```bash
set GOOGLE_APPLICATION_CREDENTIALS=media/GCP_account_keys/port-v2-service-account-key.json
```

### DB復元参考
django-dbbackupを使用：
https://djangobrothers.com/blogs/djang_dbbackup/
DUMPファイルを使用してSQLite3からPostgresSQLに移行：
https://beecoder.org/ja/django/how-to-migrate-data-from-sqlite-to-postgresql-in-django-in-django

```bash
python3 manage.py dumpdata > datadump.json
```
```bash
python3 manage.py migrate --run-syncdb
```
```bash
python3 manage.py shell
```
```bash
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
```
```bash
python3 manage.py loaddata datadump.json
```
