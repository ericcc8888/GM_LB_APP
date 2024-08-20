import os, sys

def get_api_keys():

    api_keys_name = ['LINE_BOT_ACCESS_TOKEN',
                    'LINE_BOT_SECRET',
                    'GOOGLEMAPS_API_KEY']
    
    keys = dict()

    for api_key_name in api_keys_name:
        api_key =os.getenv(api_key_name , None)
        
        if api_key is None:
            print(f'Specify {api_key}  as environment variable.')
            sys.exit(1)

        keys[api_key_name] = api_key

    return keys