from django.conf import settings
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status
from .serializer import ContactSerializer
from .models import Contact
from . import send_mail_message

import slackweb


# 問い合わせ情報取得のView(GET:全件、POST:1件のみ)
class ContactListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request, format=None):
        try:
            contact = Contact.objects.all()
            return Response(data={'contact': contact}, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response(data=[], status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response = []
        contact = Contact.objects.get(id=request.data['id'])
        return Response(data={'contact': contact}, status=status.HTTP_200_OK)


# 問い合わせ情報作成のView(POST)
class ContactRegister(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def post(self, request, format=None):

        name = request.data['name']
        email = request.data['email']
        types = request.data['type']
        content = request.data['content']

        Contact.objects.create(
            name=name,
            email=email,
            type=types,
            content=content,
        )

        slack_url = settings.SLACK_URL

        notification = f'''
<@U02CTN73EUV> <@U034YK356MT>
サイトから問い合わせがありました
氏名：{name}
メールアドレス：{email}
問い合わせ項目：{types}
内容：{content}
'''

        slack = slackweb.Slack(slack_url)
        slack.notify(text=notification)

        subject = "問い合わせいただきありがとうございます。"
        message_text = f'''
1~3営業日以内に返信いたします。しばらくお待ちください。


---------------------------
公式ライバー事務所SHIP
HP：https://ship-liver.com/
問い合わせ先：support@konome.co.jp
運営会社：株式会社このめ
会社HP：https://konome.co.jp/
会社所在地：東京都品川区西品川 1丁目1番地1号 住友不動産大崎ガーデンタワー9階
代表取締役：根岸賢伍
'''

        send_mail_message.send_gmail(email, subject, message_text)

        notification = f'''
氏名：{name}
メールアドレス：{email}
問い合わせ項目：{types}
内容：{content}
'''

        # zendeskにも送信
        send_mail_message.send_gmail("support@konome.zendesk.com", "LPから問い合わせがありました", notification)

        return Response(data={
            'name': name,
            'email': email,
            'type': types,
            'content': content,
        }, status=status.HTTP_200_OK)
