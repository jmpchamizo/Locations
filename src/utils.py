import json, requests, os, math, folium
import numpy as np
import pandas as pd
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster
from dotenv import load_dotenv
from pymongo import MongoClient
from geopy.distance import distance


def sum_funding_rounds(funding_rounds):
    currency_dict = {"USD":1, "EUR":1.09, "GBP":1.29, "CAD":0.75, "SEK":0.1, "JPY":0.0091}
    result = []
    for e in funding_rounds:
        result.append(sum([0 if k["raised_amount"] == None else k["raised_amount"]*currency_dict[k["raised_currency_code"]] for k in e if "raised_amount" in k.keys() and "raised_currency_code" in k.keys()]))
    return result



def asGeoJSON(lat,lng):
    try:
        lat = float(lat)
        lng = float(lng)
        if not math.isnan(lat) and not math.isnan(lng):
            return {
                "type":"Point",
                "coordinates":[lng,lat]
            }
    except Exception:
        print("Invalid data")
        return None


def create_document(database, json_document, new_collection, geoindex=False):
    client = MongoClient("mongodb://localhost/")
    db = client[database]
    db[new_collection].drop()
    companies_clean = db[new_collection]
    with open(json_document) as f:
        file_data = json.load(f)
    companies_clean.insert_many(file_data)
    if geoindex:
        companies_clean.create_index([("location", "2dsphere")])
    client.close()



def geocode(address):
    data = requests.get(f"https://geocode.xyz/{address}?json=1").json()
    return {
        "type":"Point",
        "coordinates":[float(data["longt"]),float(data["latt"])]
    }



def withGeoQuery(location,maxDistance=10000,minDistance=0,field="location"):
    return {
       field: {
         "$near": {
           "$geometry": location if type(location)==dict else geocode(location),
           "$maxDistance": maxDistance,
           "$minDistance": minDistance
         }
       }
    }


def get_json_locations(latitude=40.42953, longitude=-3.67932, word_key="", radius=25000, limit=1):
    load_dotenv()
    URL = 'https://api.foursquare.com/v2/venues/explore'
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    VERSION = "20180323"
    
    params = dict(
      client_id = CLIENT_ID,
      client_secret = CLIENT_SECRET,
      v = VERSION,
      ll=f"{latitude},{longitude}",
      query=word_key,
      radius= radius,
      limit=limit
    )
    
    resp = requests.get(url=(URL), params=params)
    return json.loads(resp.text)


def find_services(services, lat, long, radius=30000, limit=1):
    serv = [get_json_locations(lat, long, e, radius, limit) for e in services]
    serv_dfs = [pd.DataFrame(e["response"]["groups"][0]["items"]) for e in serv]
    serv_final = []
    for i,e in enumerate(serv_dfs):
        if "venue" in e.keys():
            if type(serv_final) == list:
                serv_final = pd.DataFrame(columns = e.venue[i].keys())
            for v in e.venue:
                serv_final = serv_final.append(v, ignore_index = True)
    return serv_final



def get_coordinates(city="", airport=False, companies=[], services=[], radius=30000, limit=10):
    coord = geocode(city)["coordinates"]
    serv_dfs = find_services(services, coord[1], coord[0], radius, limit)
    return serv_dfs

def get_distance(a):
    return lambda b: (distance((list(a["latitude"])[0], list(a["longitude"])[0]), (b.latitude, b.longitude))).km


def get_distance2(a):
    return lambda b: (distance((list(a["latitude"])[0], list(a["longitude"])[0]), (b["location"]["lat"], b["location"]["lng"]))).km


def calculate_service_distance(source, service_df):
    for df in service_df:
        df["distance"] = df[["location"]].apply(get_distance2(source), axis=1)


def calculate_distance(source, dataframe):
    for df in dataframe:
        df["distance"] = df[["latitude","longitude"]].apply(get_distance(source), axis=1)   



def calculate_point(services, companies):
    points = get_points_service(services)
    point_service = aux_calculate_point(points)
    points = get_points_companies(companies)
    point_companie = aux_calculate_point(points)
    return [calculate_midle_point(point_companie[0], point_service[0]), calculate_midle_point(point_companie[1], point_service[1])]

def calculate_midle_point(a, b):
    return (a+b)/2

def aux_calculate_point(points = []):
    point = [0,0]
    if len(points) == 1:
        return points[0]
    temp = []
    for i,_ in enumerate(points):
        if i == 0:
            continue
        point[0] = calculate_midle_point(points[i-1][0],points[i][0])
        point[1] = calculate_midle_point(points[i-1][1],points[i][1])
        temp.append(point)
    return aux_calculate_point(temp)

def get_points_service(df):
    point = [0,0]
    points = []
    for i,_ in enumerate(df):
        point[0] = df[i].loc[0]["location"]["lat"]
        point[1] = df[i].loc[0]["location"]["lng"]
        points.append(point)
    return points

def get_points_companies(df):
    point = [0,0]
    points = []
    for i,_ in enumerate(df):
        point[0] = df[i].loc[0]["latitude"]
        point[1] = df[i].loc[0]["longitude"]
        points.append(point)
    return points


def create_new_df(df):
    temp = pd.DataFrame(columns=["name", "latitude", "longitude"])
    for i in range(df.shape[0]):
        temp.loc[i] = [df.name[i], df.loc[i]["location"]["lat"], df.loc[i]["location"]["lng"]]
    return temp 



def locate(city, marker , services=[], companies=[]):
    start_lat = city["coordinates"][1]
    start_lon = city["coordinates"][0]
    heat_m = folium.Map(location=[start_lat, start_lon],tiles='cartodbpositron', zoom_start=15)
    Marker([marker["lat"], marker["long"]], icon=folium.Icon(color='red')).add_to(heat_m)
    colors = ['green', 'black', 'darkpurple', 'pink', 'blue', 'darkgreen']
    for j,s in enumerate(services):
        for i in range(s.shape[0]):
            heat_m.add_child(Marker([s.loc[i]["location"]["lat"], s.loc[i]["location"]["lng"]], icon=folium.Icon(color=colors[j])))
    for j,c in enumerate(companies):
        j += 4
        for i in range(c.shape[0]):
            heat_m.add_child(Marker([c.loc[i]["latitude"], c.loc[i]["longitude"]], icon=folium.Icon(color=colors[j])))
    return heat_m