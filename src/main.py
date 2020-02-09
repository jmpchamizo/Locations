import json, requests, os
from dotenv import load_dotenv





#def get_json_location(v, geolocation, word_key, limit)
def get_json_locations():
    URL = 'https://api.foursquare.com/v2/venues/explore'
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    params = dict(
      client_id=client_id,
      client_secret=client_secret,
      v='20180323',
      #v=v,
      ll='40.7243,-74.0018',
      #ll=geolocation,
      query="design",
      limit=1
    )
    resp = requests.get(url=(URL), params=params)
    return json.loads(resp.text)


print(get_json_locations())
