import requests
from time import sleep

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""
MAX_SCORE = 2400

s = requests.session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://steamcommunity.com/saliengame/play/',
    'Origin': 'https://steamcommunity.com',
    'Accept': '*/*'
    })


def get_zone():
    data = {'active_only': 1}
    result = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanets/v0001/", params=data)
    if result.status_code != 200:
        print("Get planet errored... trying again")
        get_zone()
    json_data = result.json()
    for planet in json_data["response"]["planets"]:
        info_data = {'id': planet["id"]}
        info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
        if info.status_code != 200:
            print("Get planet errored... trying the next planet")
            continue
        info_json = info.json()
        for zone in info_json["response"]["planets"][0]["zones"]:
            if zone["difficulty"] == 3 and not zone["captured"] and zone["capture_progress"] < 0.8:
                return zone["zone_position"]


def join_zone(zone):
    data = {
        'zone_position': zone,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Join zone errored... trying again")
        play_game()
    else:
        print("Joined zone: " + str(result.json()["response"]["zone_info"]["zone_position"]))


def report_score():
    data = {
        'access_token': TOKEN, 
        'score': MAX_SCORE, 
        'language':'english'
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportScore/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Report score errored... trying again")
        play_game()
    else:
        print(result.json()["response"])


def play_game():
    print("Finding a zone")
    zone = get_zone()
    while(1):
        join_zone(zone)
        print("Sleeping for 1 minute 50 seconds")
        sleep(110)
        report_score()

while(1):
    try:
        play_game()
    except:
        continue