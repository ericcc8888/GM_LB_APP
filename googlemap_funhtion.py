# import googlemaps   ##導入googlemaps模組

# gmaps = googlemaps.Client(key='AIzaSyANzenmkUxcDLd7jGwvo676-qD-8YdMoM0') ##利用API建立客戶端

# # Geocoding an address
# geocode_result = gmaps.geocode('Taiwan')[0] ##利用Geocode函數進行定位
# location = geocode_result['geometry']['location'] #取得定位後經緯度

# print(location)


# #location回傳格式如下圖，可依照格式自訂義變數，就不用調用Geodcode API

# # Search for places
# #(keyword參數="輸入你想查詢的物件",radius="公尺單位")

# places_result = gmaps.places_nearby(location,type='restaurant', radius=50000)

# ##列印出地點的名稱與地點
# for place in places_result['results']:
#     print(place['name'], place['vicinity']) 


from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, LocationMessage,TextSendMessage

import os
import sys

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_BOT_SECRET', None)
channel_access_token = os.getenv('LINE_BOT_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_BOT_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_BOT_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

line_bot_api = LineBotApi(channel_access_token)

configuration = Configuration(
    access_token=channel_access_token
)

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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

# 处理 LocationMessage 事件
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 从事件中提取位置信息
    location = event.message

    # 打印位置数据
    print(f"地点名称: {location.title}")
    print(f"地址: {location.address}")
    print(f"纬度: {location.latitude}")
    print(f"经度: {location.longitude}")

    # 可以根据需求，做其他处理，比如回复用户消息
    reply_message = f"你的位置: {location.title} ({location.address})\n纬度: {location.latitude}\n经度: {location.longitude}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run(debug=True)