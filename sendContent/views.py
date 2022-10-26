from django.http import HttpResponse, Http404
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import TwitterSendContentSerializer
from .models import TwitterSendContent
from sender.models import TwitterSender
from user.models import User


# TwitterDM送信文情報取得のView(GET=ログインユーザー, POST=指定アカウント)
class TwitterSendContentListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendContent.objects.all()
    serializer_class = TwitterSendContentSerializer

    def get(self, request, format=None):
        response = []
        user = User.objects.get(email=request.user.email)
        send_contents = TwitterSendContent.objects.filter(user=user)
        response = getSendContentResponse(send_contents)
        return Response(data=response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response = []
        user = User.objects.get(uuid=request.data['data'])
        send_contents = TwitterSendContent.objects.filter(user=user)
        response = getSendContentResponse(send_contents)
        return Response(data=response, status=status.HTTP_200_OK)


# TwitterDM送信文情報取得のView(POST)
class TwitterSendContentRegister(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TwitterSendContent.objects.all()
    serializer_class = TwitterSendContentSerializer

    def post(self, request, format=None):
        user = {}
        try:
            if len(request.data['sendContent']['uuid']) > 0:
                user = User.objects.get(uuid=request.data['sendContent']['uuid'])
        except KeyError:
            user = User.objects.get(email=request.user.email)
        sender_screen_list = request.data['sendContent']['screen_names']
        content = request.data['sendContent']['content']
        for sender_screen in sender_screen_list:
            sender = TwitterSender.objects.get(screen_name=sender_screen)
            twitterSendContent = TwitterSendContent.objects.create(
                content=content
            )
            twitterSendContent.user.add(user)
            twitterSendContent.sender.add(sender)
        return Response(data={
            'message': 'DM送信文作成成功',
        }, status=status.HTTP_201_CREATED)


# Twitter DM送信文更新のView(PUT)
class TwitterSendContentUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TwitterSendContentSerializer
    queryset = TwitterSender.objects.all()

    def put(self, request, format=None):
        try:
            user = User.objects.get(email=request.user.email)
            twitterSendContent = TwitterSendContent.objects.get(user=user)
            twitterSendContent.content = request.data['sendContent']['content']
            for screen_name in request.data['sendContent']['screen_names']:
                if '@' in screen_name:
                    screen_name = screen_name.replace('@', '')
                sender = TwitterSender.objects.get(screen_name=screen_name)
                twitterSendContent.sender.add(sender)
            twitterSendContent.save()
            return Response(data={
                'message': 'Twitter DM送信文更新完了',
            }, status=status.HTTP_200_OK)
        except TwitterSender.DoesNotExist:
            raise Http404


# TwitterDM送信アカウント削除のView(DELETE)
class TwitterSenderDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TwitterSendContentSerializer
    queryset = TwitterSendContent.objects.all()

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.uuid)
            return instance
        except TwitterSendContent.DoesNotExist:
            raise Http404


def getSendContentResponse(send_contents):
    response = []
    for send_content in send_contents:
        senders = send_content.sender.all()
        screen_names = []
        for sender in senders:
            screen_name = '@' + sender.screen_name
            screen_names.append(screen_name)
        res = {
            'content': send_content.content,
            'screen_names': screen_names
        }
        response.append(res)
    return response
