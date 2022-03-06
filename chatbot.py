from email import message
from tkinter import Message
from typing import List
import spacy
import googlemaps
import requests
api_key = "83c9f290b48d7b2b44670e567e4fd0a1"


def get_weather(city_name):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
        city_name, api_key)
    response = requests.get(api_url)
    response_dict = response.json()
    weather = response_dict["weather"][0]["description"]
    if response.status_code == 200:
        return weather
    else:
        print('[!] HTTP {0} calling [{1}]'.format(
            response.status_code, api_url))
        return None


def get_Geocoding(city_name):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
        city_name, api_key)


def get_address(location):
    gmaps = googlemaps.Client(key='AIzaSyAkkUyaAPdWgYJf252NIzgphIXWv6gRmPI')

    # Geocoding an address
    geocode_result = gmaps.geocode(location)
    # print(geocode_result)
    return geocode_result[0]["formatted_address"]


def get_coord(cityname: str):
    api_key = "83c9f290b48d7b2b44670e567e4fd0a1"
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
        cityname, api_key)
    response = requests.get(api_url)
    response_dict = response.json()
    lon = response_dict["coord"]["lon"]
    lat = response_dict["coord"]["lat"]
    return lon, lat


def get_places(lon: float, lat: float, radius: int = 200):
    api_key = "5ae2e3f221c38a28845f05b6de91a85d0a0cb7bc81635bd0c54a8bdc"
    api_url = f"http://api.opentripmap.com/0.1/ru/places/radius?lon={lon}&lat={lat}&apikey={api_key}&radius={radius}"

    payload = {}
    headers = {}

    response = requests.request("GET", api_url, headers=headers, data=payload)
    response_dict = response.json()
    locations = response_dict["features"][0:3]
    places = [(item["properties"]["name"], item["properties"]["kinds"])
              for item in locations]
    return places


# get_address("Quality Hotel Panorama")
# get_weather("Trondheim")
nlp = spacy.load("en_core_web_md")
# statement1 = nlp("Current weather in a city")
# statement2 = nlp("What is the location in?")
# print(statement1.similarity(statement2))

weather_sentances = {"Current weather in a city",
                     "What's the weather forecast for the city", "How's the weather in a city?"}
restaurant_sentances = {"It is Street",
                        "where is the restaurant?", "restaurants near me"}
place_sentances = {
    " Beautiful Places to Visit in city ", "most popular places in city "}
Finish_sentances = {
    "grateful", "I appreciate you"}
#    "Tourisyt Attractions in city",
# flight_sentances = {" What is the next bus?", "I want to go to city on date"}
domains = {'weather', 'restaurant', 'place', "finish"}


def get_avg_similarity(statement, dic_sentances):
    sum = 0
    for sentance in dic_sentances:
        statement_domain = nlp(sentance)
        statement_pure = nlp(statement)
        similarity_score = statement_domain.similarity(statement_pure)
        sum += similarity_score
    return sum/len(dic_sentances)


def get_similarity(domain, statement):
    if domain == "weather":
        return get_avg_similarity(statement=statement, dic_sentances=weather_sentances)

    if domain == 'restaurant':
        return get_avg_similarity(statement=statement, dic_sentances=restaurant_sentances)

    if domain == 'place':
        return get_avg_similarity(statement=statement, dic_sentances=place_sentances)

    if domain == 'finish':
        return get_avg_similarity(statement=statement, dic_sentances=Finish_sentances)
    # if domain == 'flight':
    #     return get_avg_similarity(statement=statement, dic_sentances=flight_sentances)


def Find_domain(statement):
    max = 0
    res_domain = ''
    for domain in domains:
        score = get_similarity(domain, statement)
        if max <= score:
            max = score
            res_domain = domain
    return res_domain


class Flight:
    form = ""
    to = ""
    time = ""
    day = ""
    flightname = ""


class Place:
    name: str
    kind: list
    address: str


class Memory:
    cityname: str = ""
    lon: float = 0
    lat: float = 0
    places: List[Place] = []
    weather: str = ""


def weather(statement, memory: Memory):
    statement = nlp(statement)
    for ent in statement.ents:
        # ent means noun
        if ent.label_ == "GPE":
            city = ent.text
            break
        else:
            return "You need to tell me a city to check."
    memory.cityname = city
    city_weather = get_weather(city)
    if city_weather is not None:
        return "In " + city + ", the current weather is: " + city_weather
    else:
        return "Something went wrong."


def place(statement, memory: Memory):
    statement = nlp(statement)
    if memory.cityname is None or memory.cityname == "":
        for ent in statement.ents:
            if ent.label_ == "GPE":
                memory.cityname = ent.text
                break
            else:
                return "You need to tell me a city to check."
    message = ""
    if memory.lat is None or memory.lat == 0 or memory.lon is None or memory.lon == 0:
        lon, lat = get_coord(memory.cityname)
        memory.lat = lat
        memory.lon = lon
    places = get_places(memory.lon, memory.lat)
    for name, kinds in places:
        kind = kinds.split(",")[0]
        message += f"name: {name} , kind = {kind} \n"

    return message


def restaurant(statement):
    statement = nlp(statement)
    restaurant_name = ""
    for token in statement:
        if token.tag_ == "NNP" and token.is_stop == False:
            restaurant_name += " " + token.text

    restaurant_name = restaurant_name.strip()
    restaurant_address = get_address(restaurant_name)
    if restaurant_address is not None:
        return "it is at " + restaurant_address
    else:
        return "Something went wrong."


def flight(statement, obj_flight: Flight):
    statement = nlp(statement)
    cities = []
    dates = []
    times = []
    for ent in statement.ents:
        if ent.label_ == 'GPE':
            if len(cities) < 1:
                cities.append(ent)
        if ent.label_ == 'DATE':
            if len(dates) != 0:
                dates.append(ent)
        if ent.label_ == 'CARDINAL':
            if len(times) != 0:
                times.append(ent)
    try:
        obj_flight.form = cities[0]
    except:
        pass
    try:
        obj_flight.to = cities[1]
    except:
        pass
    try:
        obj_flight.day = dates[0]
    except:
        pass
    try:
        obj_flight.time = times[0]
    except:
        pass

    if obj_flight.form == "":
        return 400, "Enter the origin of the flight?"
    if obj_flight.to == "":
        return 400, "Enter the flight destination?"
    if obj_flight.day == "":
        return 400, "Enter the flight day?"
    if obj_flight.time == "":
        return 400, "Enter the flight time?"


def chatbot():
    flag = True
    message = " how can i help you: \n"
    memory = Memory()
    while(flag):
        statement = input(message)
        domain = Find_domain(statement)
        print(domain)
        if domain == "weather":
            message = weather(statement, memory)
            message += "\n Do you need anything else? \n"
            flag = True
        elif domain == "restaurant":
            message = restaurant(statement)
            message += "\n Do you need anything else? \n"
            flag = True
        elif domain == "place":
            message = place(statement, memory)
            message += "\n Do you need anything else? \n"
            flag = True
        elif domain == "flight":
            obj_flight = Flight()
            status, message = flight(statement, obj_flight)
            if status == 400:
                flag = True
            else:
                flag = False
        elif domain == "finish":
            flag = False
        else:
            print("i dont have your answer")
            flag = False


# chatbot("where is the Boutary restaurant")
# chatbot('Is it going to rain in stockholm today?')
# chatbot('what is the next flight from gothenburg to stockholm on monday after 12')
chatbot()
