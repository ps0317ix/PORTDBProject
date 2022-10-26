from django.db import transaction
from django.http import HttpResponse, Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserSerializer, LiverSerializer
from .models import User


# 全クライアント情報取得のView(GET)
class GetClientListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.filter(is_admin=False)
    serializer_class = UserSerializer


# 全ライバー情報取得のView(GET)
class GetLiverListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.filter(is_liver=True)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        livers = User.objects.filter(is_liver=True)
        res = []
        for liver in livers:
            obj = {
                'id': liver.uuid,
                'uuid': liver.uuid,
                'username': liver.username,
                'email': liver.email,
                'birthday': liver.birthday.strftime('%m%d'),
                'hobby': liver.hobby,
                'genre': liver.genre,
                'line_id': liver.line_id,
                'start_live_date': liver.start_live_date,
                'responsible_manager': liver.responsible_manager,
                'liver_kinds': liver.liver_kinds,
                'profession': liver.profession,
                'prefecture': liver.prefecture,
                'is_sent_dm_type': liver.is_sent_dm_type,
                'live_app': liver.live_app,
                'referral': liver.referral,
                'liver_id': liver.liver_id,
                'real_name': liver.real_name,
                'rank': liver.rank,
                'sex': liver.sex,
                'message': liver.message,
                'image_1': liver.image_1.name,
                'image_2': liver.image_2.name,
                'image_3': liver.image_3.name,
                'is_active': liver.is_active,
                'created_at': liver.date_joined
            }
            res.append(obj)

        response = {'res': res}
        return Response(response, status=status.HTTP_200_OK)


# 全ライバー情報取得のView(GET)
class GetPopularLiverListView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.filter(is_liver=True)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        livers = User.objects.filter(is_liver=True, rank="S")
        res = []
        for liver in livers:
            obj = {
                'id': liver.uuid,
                'uuid': liver.uuid,
                'username': liver.username,
                'email': liver.email,
                'birthday': liver.birthday.strftime('%m%d'),
                'hobby': liver.hobby,
                'genre': liver.genre,
                'line_id': liver.line_id,
                'start_live_date': liver.start_live_date,
                'responsible_manager': liver.responsible_manager,
                'liver_kinds': liver.liver_kinds,
                'profession': liver.profession,
                'prefecture': liver.prefecture,
                'is_sent_dm_type': liver.is_sent_dm_type,
                'live_app': liver.live_app,
                'referral': liver.referral,
                'liver_id': liver.liver_id,
                'real_name': liver.real_name,
                'sex': liver.sex,
                'message': liver.message,
                'image_1': liver.image_1.name,
                'image_2': liver.image_2.name,
                'image_3': liver.image_3.name,
                'is_active': liver.is_active,
                'rank': liver.rank,
                'created_at': liver.date_joined
            }
            res.append(obj)
        response = {'res': res}
        return Response(response, status=status.HTTP_200_OK)


# ユーザ作成のView(POST)
class UserRegister(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, format=None):
        user = request.data
        user['is_staff'] = True
        user['is_liver'] = False
        serializer = UserSerializer(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(data={
                'message': 'クライアント作成完了',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ライバー作成のView(POST)
class LiverRegister(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = LiverSerializer

    @transaction.atomic
    def post(self, request, format=None):
        user = request.data
        serializer = LiverSerializer(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(data={
                'message': 'ライバー作成完了',
            }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.error_messages)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ユーザ情報取得のView(GET)
class UserGetView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        roles = []
        if request.user.is_admin:
            roles.append('admin')
        else:
            roles.append('editor')
        return Response(data={
            'username': request.user.username,
            'email': request.user.email,
            'profile': request.user.profile,
            'roles': roles,
            'avatar': 'avatar',
            'introduction': 'introduction',
            'message': 'ログイン成功',
            },
            status=status.HTTP_200_OK)


# ユーザ情報更新のView(PUT)
class UserUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def put(self, request, format=None):
        try:
            user = User.objects.get(uuid=request.data['id'])
            user.username = request.data['username']
            user.email = request.data['email']
            user.is_active = request.data['is_active']
            user.save()
            return Response(data={
                'message': '更新完了',
            },
                status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise Http404


# ライバー情報更新のView(PUT)
class LiverUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def put(self, request, format=None):
        try:
            user = User.objects.get(uuid=request.data['id'])
            user.username = request.data['username']
            user.email = request.data['email']
            user.birthday = request.data['birthday']
            user.hobby = request.data['hobby']
            user.genre = request.data['genre']
            user.message = request.data['message']
            user.line_id = request.data['line_id']
            user.is_active = request.data['is_active']
            user.start_live_date = request.data['start_live_date']
            user.responsible_manager = request.data['responsible_manager']
            user.liver_kinds = request.data['liver_kinds']
            user.profession = request.data['profession']
            user.prefecture = request.data['prefecture']
            user.is_sent_dm_type = request.data['is_sent_dm_type']
            user.live_app = request.data['live_app']
            user.referral = request.data['referral']
            user.liver_id = request.data['liver_id']
            user.real_name = request.data['real_name']
            user.sex = request.data['sex']
            user.rank = request.data['rank']
            user.save()
            return Response(data={'message': '更新完了'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise Http404


class LiverImage1Register(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, format=None, uuid=None):
        user = self.queryset.get(pk=uuid)
        user.image_1 = request.data['image']
        user.save()
        return Response(data={'message': '更新完了'}, status=status.HTTP_200_OK)


class LiverImage2Register(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, format=None, uuid=None):
        user = self.queryset.get(pk=uuid)
        user.image_2 = request.data['image']
        user.save()
        return Response(data={'message': '更新完了'}, status=status.HTTP_200_OK)


class LiverImage3Register(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, format=None, uuid=None):
        user = self.queryset.get(pk=uuid)
        user.image_3 = request.data['image']
        user.save()
        return Response(data={'message': '更新完了'}, status=status.HTTP_200_OK)


# ユーザのアバター情報更新のView(PUT)
class UserUpdateAvatarView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def put(self, request, format=None):
        try:
            user = self.queryset.get(pk=request.user.uuid)
            user.avatar = request.data['avatar']
            user.save()
            return Response(data={
                'message': 'アップロード成功',
            },
                status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise Http404


# ユーザ削除のView(DELETE)
class UserDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def delete(self, request, format=None):
        try:
            user = User.objects.get(uuid=request.data['uuid'])
            user.delete()
            return Response(data={
                'message': '削除完了',
            },
                status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise Http404
