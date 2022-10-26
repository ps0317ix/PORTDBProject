from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse, Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import ServerSerializer
from .models import Server
from sendDM.requestSendDM import server_health_check_main

import schedule
import requests
from time import sleep

headers = {
    'Content-Type': 'application/json',
}


# 全サーバー情報取得のView(GET)
class GetServerListView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


# サーバーヘルスチェックのView(GET)
class GetServerHealthCheck(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, format=None):
        for server in Server.objects.all():
            url = f'{server.base_url}'
            response = requests.get(url, auth=(server.basic_user, server.basic_password))
            print(f'{server.name}:{response.status_code}')
            if response.status_code == 200:
                server.is_active = True
                server.save()
            else:
                server.is_active = False
                server.save()

        res = []
        for server in Server.objects.all():
            obj = {
                'id': server.id,
                'name': server.name,
                'base_url': server.base_url,
                'basic_user': server.basic_user,
                'basic_password': server.basic_password,
                'is_active': server.is_active,
                'created_at': server.created_at,
                'updated_at': server.updated_at
            }
            res.append(obj)

        return Response(data={'res': res}, status=status.HTTP_200_OK)


# 定期実行サーバーヘルスチェックのView(GET)
class GetScheduleServerHealthCheck(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, format=None):
        schedule.every(10).minutes.do(server_health_check_main)
        while True:
            try:
                schedule.run_pending()
                sleep(1)
            except Exception as e:
                return Response(data={'message': e}, status=status.HTTP_400_BAD_REQUEST)


# サーバー作成のView(POST)
class ServerRegister(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    @transaction.atomic
    def post(self, request, format=None):
        try:
            server = request.data['server']
            try:
                basic_user = server['basic_user']
            except Exception as e:
                print(e)
            serializer = Server.objects.create(
                name=server['name'],
                base_url=server['base_url'],
                basic_user=basic_user,
                basic_password=server['basic_password'],
            )
            return Response(data={'message': 'サーバー登録成功'}, status=status.HTTP_201_CREATED)
        except Server.DoesNotExist:
            return Response(data={'message': '登録失敗'}, status=status.HTTP_400_BAD_REQUEST)


# サーバー情報取得のView(GET)
class ServerGetView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, format=None):
        return Response(data={
            'username': request.user.username,
            'email': request.user.email,
            'profile': request.user.profile,
            'company': request.user.company,
            'avatar': 'avatar',
            'introduction': 'introduction',
            'message': 'ログイン成功',
            },
            status=status.HTTP_200_OK)


# サーバー情報更新のView(PUT)
class ServerUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServerSerializer
    queryset = Server.objects.all()

    def put(self, request, format=None):
        try:
            server = Server.objects.get(pk=request.data['server']['id'])
            server.name = request.data['server']['name']
            server.base_url = request.data['server']['base_url']
            server.basic_user = request.data['server']['basic_user']
            server.basic_password = request.data['server']['basic_password']
            server.is_active = request.data['server']['is_active']
            server.save()
            return Response(data={
                'message': 'サーバー情報更新完了',
            }, status=status.HTTP_201_CREATED)
        except Server.DoesNotExist:
            raise Http404


# サーバー削除のView(DELETE)
class ServerDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServerSerializer
    queryset = Server.objects.all()

    def delete(self, request, format=None):
        try:
            server = Server.objects.get(pk=request.data['server']['id'])
            server.delete()
            return Response(data={
                'message': 'サーバー削除完了',
            }, status=status.HTTP_200_OK)
        except Server.DoesNotExist:
            raise Http404
