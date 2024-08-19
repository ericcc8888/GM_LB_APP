from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, LocationMessage, TextSendMessage ,FlexSendMessage
from linebot.models.flex_message import BubbleContainer, TextComponent, BoxComponent
from linebot.exceptions import InvalidSignatureError

from API_KEYS import get_api_keys
from flex_message_formmat import locations_flexmessage
import sys

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
keys = get_api_keys()
channel_secret = keys['LINE_BOT_SECRET']
channel_access_token = keys['LINE_BOT_ACCESS_TOKEN']
if channel_secret is None:
    print('Specify LINE_BOT_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_BOT_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)
line_bot_api = LineBotApi(channel_access_token)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#==============================================================

#處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # reply_text = TextSendMessage(text=event.message.text)

    # # 使用 reply_message 方法回應使用者
    # line_bot_api.reply_message(event.reply_token, reply_text)

    if event.message.text == "美食":
        flex_message = FlexSendMessage(
        alt_text='This is a Flex Message',
        contents= locations_flexmessage()
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    else:
        reply_text = TextSendMessage(text=event.message.text)

        # 使用 reply_message 方法回應使用者
        line_bot_api.reply_message(event.reply_token, reply_text)

#==============================================================

#處理位置訊息
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    location = event.message

    # 可以根据需求，做其他处理，比如回复用户消息
    reply_text = TextSendMessage(text=f"你的位置: {location.title} ({location.address})\n纬度: {location.latitude}\n经度: {location.longitude}")

    # 使用 reply_message 方法回應使用者
    line_bot_api.reply_message(event.reply_token, reply_text)

#==============================================================

if __name__ == "__main__":
    app.run(debug=True)