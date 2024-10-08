from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, LocationMessage, TextSendMessage ,FlexSendMessage, PostbackEvent, RichMenuBounds, RichMenu, RichMenuSize, RichMenuArea, PostbackAction
from linebot.exceptions import InvalidSignatureError

from API_KEYS import get_api_keys
from line_flex import line_store_flex, flex_formmat, rice_class, noodle_class, dessert_class, exotic_cuisine_class
import sys,googlemaps,requests

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
user_states = {}
#處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_states
    user_id = event.source.user_id
    user_states[user_id] = event.message.text  # 保存用戶的偏好
    text = "請傳送主人的定位資訊"
    text_message = TextSendMessage(text)
    line_bot_api.reply_message(event.reply_token, text_message)

#==============================================================

#處理位置訊息
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    user_states
    user_id = event.source.user_id
    location = event.message
    need_food = user_states.get(user_id, None)  # 獲取用戶的偏好
    if not need_food:
        # 如果用戶沒有先輸入食物類型，提示用戶輸入
        text_message = TextSendMessage(text="請先告訴小食主人想吃什麼，然後再傳送您的定位資訊。")
        line_bot_api.reply_message(event.reply_token, text_message)
    else:
        flex_message = FlexSendMessage(
            alt_text='This is a Flex Message',
            contents=get_store_info(location, need_food)
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

#==============================================================

def upload_rich_menu_image(line_bot_api, rich_menu_id, image_path):
    with open('static/rich_menu.jpeg', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)

def create_rich_menu():
    # 创建主菜单
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Main Menu",
        chat_bar_text="請點擊開始使用隨食即行",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=59, y=34, width=1140, height=827),
                action=PostbackAction(data="action=first_layer_url")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1284, y=8, width=1191, height=853),
                action=PostbackAction(data="action=first_layer_location")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=63, y=874, width=1136, height=794),
                action=PostbackAction(data="action=first_layer_location")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1288, y=874, width=1187, height=807),
                action=PostbackAction(data="action=location_option1")
            ),
        ]
    )

    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    # 上传并设置图片，使用您上传的图片路径
    upload_rich_menu_image(line_bot_api, rich_menu_id, 'static/rich_menu.jpeg')

    # 设置为默认的 Rich Menu
    line_bot_api.set_default_rich_menu(rich_menu_id)

    print(f"Rich menu created and set as default: {rich_menu_id}")
#==============================================================

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    #if data == "action=first_layer_text":
        #flex_message = FlexSendMessage(alt_text="地區選擇", contents=locations_flexmessage())
        #line_bot_api.reply_message(event.reply_token, flex_message)
    if data == "action=first_layer_url":
        flex_message = FlexSendMessage(alt_text="米飯類選擇", contents=rice_class())
        line_bot_api.reply_message(event.reply_token, flex_message)
        text = "請點選圖卡告訴我你想吃甚麼飯，上述沒有想吃的也可以打字輸入呦"
        text_message = TextSendMessage(text)
        line_bot_api.push_message(event.source.user_id, text_message)
        
    elif data == "action=first_layer_location":
        flex_message = FlexSendMessage(alt_text="麵類選擇", contents=noodle_class())
        line_bot_api.reply_message(event.reply_token, flex_message)
        text = "請點選圖卡告訴我你想吃甚麼麵，上述沒有想吃的也可以打字輸入呦"
        text_message = TextSendMessage(text)
        line_bot_api.push_message(event.source.user_id, text_message)

    elif data == "action=location_option1":
        flex_message = FlexSendMessage(alt_text="甜點選擇", contents=dessert_class())
        line_bot_api.reply_message(event.reply_token, flex_message)
        text = "請點選圖卡告訴我你想吃甚麼點心，上述沒有想吃的也可以打字輸入呦"
        text_message = TextSendMessage(text)
        line_bot_api.push_message(event.source.user_id, text_message)

    elif data == "action=location_option2":
        flex_message = FlexSendMessage(alt_text="異國料理選擇", contents=exotic_cuisine_class())
        line_bot_api.reply_message(event.reply_token, flex_message)
        text = "請點選圖卡告訴我你想吃甚麼風格的料理，上述沒有想吃的也可以打字輸入呦"
        text_message = TextSendMessage(text)
        line_bot_api.push_message(event.source.user_id, text_message)
    
#==============================================================

def get_store_info(location, need_food, max_results=10):
    # Geocoding an address
    origin_location = {'lat':location.latitude, 'lng':location.longitude}
    # 使用 Places API 搜尋附近500公尺內的餐廳
    places_result = gmaps.places_nearby(location=origin_location, radius=500, keyword=need_food, language="zh-TW")

    places_text = []
    flex_message_datas = []
    # 列印每個餐廳的名稱及經緯度
    for place in places_result['results'][:max_results]:
        name = place.get('name')  # 獲取餐廳名稱
        place_location = place['geometry']['location']  # 獲取餐廳的經緯度
        lat = place_location['lat']
        lng = place_location['lng']

        address = place.get('vicinity')
        
        # 獲取餐廳的照片,評論分數及營業時間
        place_phtot = place.get('photos',[])
        place_rate = place.get('rating')
        opening_hours = place.get('opening_hours', {}) 
        business_time = opening_hours.get('open_now', '無營業時間')

        # 獲取店家的place_id,url及電話
        place_id = place.get('place_id')
        store_result = gmaps.place(place_id) 
        googlemap_url = store_result["result"]['url'] # 獲取餐廳的url
        
        telephone = 'tel:' + store_result["result"].get("formatted_phone_number", "0000").replace(" ", "")
        

        if business_time:
            business_status = '營業中'
            business_color = "#00A600"

        else:
            business_status = '已打烊'
            business_color = "#CE0000"

        if place_phtot:
            photo_reference = place_phtot[0].get('photo_reference')
            photo_url = get_photo_url(photo_reference)
        else:
            photo_reference = ""
            photo_url = "https://www.post.gov.tw/post/internet/images/NoResult.jpg"

        # 使用 Geocoding API 獲取中文地址
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng), language='zh-TW')
        # 獲取address_components的資訊:[0]street_number(如:13號) , [1]route(如:青海路二段) , [2]administrative_area_level_3(如:逢甲里) , [3]administrative_area_level_2(如:西屯區)
        #                             [4]administrative_area_level_1(如:台中市) , [5]country(如:台灣) , [6]postal_code
        detailed_address = reverse_geocode_result[0]['address_components'][4]['long_name'] + reverse_geocode_result[0]['address_components'][3]['long_name'] + address
        places_text.append(line_store_flex(photo_url, name, place_rate, detailed_address, business_status, telephone, googlemap_url, business_color , flex_message_datas))

    flex_message = flex_formmat(places_text[0])
    print(flex_message)
    return flex_message

#==============================================================

def get_photo_url(photo_reference, max_width=400):
    """构建照片请求 URL"""
    base_url = 'https://maps.googleapis.com/maps/api/place/photo'
    params = {
        'photoreference': photo_reference,
        'maxwidth': max_width,
        'key': keys['GOOGLEMAPS_API_KEY']
    }
    url = f"{base_url}?{requests.compat.urlencode(params)}"
    return url

#==============================================================

if __name__ == "__main__":
    app.run(debug=True)