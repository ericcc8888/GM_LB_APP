from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, LocationMessage, TextSendMessage ,FlexSendMessage
from linebot.models.flex_message import BubbleContainer, TextComponent, BoxComponent
from linebot.exceptions import InvalidSignatureError

from API_KEYS import get_api_keys
from flex_message_formmat import locations_flexmessage
import sys,googlemaps

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
keys = get_api_keys()
channel_secret = keys['LINE_BOT_SECRET']
channel_access_token = keys['LINE_BOT_ACCESS_TOKEN']
gmaps = googlemaps.Client(key=keys['GOOGLEMAPS_API_KEY'])

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

    if event.message.text == "台灣美食":
        flex_message = FlexSendMessage(
        alt_text='This is a Flex Message',
        contents= locations_flexmessage()
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    else:
        reply_text = TextSendMessage(text='請輸入"台灣美食"')

        # 使用 reply_message 方法回應使用者
        line_bot_api.reply_message(event.reply_token, reply_text)

#==============================================================

#處理位置訊息
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    location = event.message
    # Geocoding an address
    origin_location = {'lat':location.latitude, 'lng':location.longitude}

    # 使用 Places API 搜尋附近500公尺內的餐廳
    places_result = gmaps.places_nearby(location=origin_location, radius=500, type='restaurant')

    places_locations = []
    for place in places_result['results']:
        place_location = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        places_locations.append(place_location)
    # 使用 Distance Matrix API 計算距離
    distances = gmaps.distance_matrix(origins=[(origin_location['lat'], origin_location['lng'])],
                                    destinations=places_locations,
                                    units='metric')

    places_text = ""
    # 列印每個餐廳的名稱、中文地址和距離
    for i, place in enumerate(places_result['results']):
        name = place.get('name')  # 獲取餐廳名稱
        place_location = place['geometry']['location']  # 獲取餐廳的經緯度
        lat = place_location['lat']
        lng = place_location['lng']
        
        # 獲取距離資訊
        distance_info = distances['rows'][0]['elements'][i]
        distance_text = distance_info.get('distance', {}).get('value', '未知')

        # 使用 Geocoding API 獲取中文地址
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng), language='zh-TW')
        
        if reverse_geocode_result:
            detailed_address = reverse_geocode_result[0]['formatted_address']
            # print(f"餐廳名稱: {name}")
            # print(f"地址: {detailed_address}")
            # print(f"距離: {distance_text}m")
            # print(f"============================================")
            places_text += f"餐廳名稱:{name}\n 地址:{detailed_address}\n 距離:{distance_text}m\n ======================\n"
        else:
            places_text += f"餐廳名稱: {name} \n 地址: 無法獲取\n 距離: {distance_text}m\n ======================\n"

    reply_text = TextSendMessage(text=places_text)
    line_bot_api.reply_message(event.reply_token, reply_text)
#==============================================================

if __name__ == "__main__":
    app.run(debug=True)