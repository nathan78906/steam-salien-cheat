import requests
import json
from time import sleep

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""

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
        print("Get planets errored... trying again(after 30s cooldown)")
        sleep(30)
        get_zone()
    json_data = result.json()
    for difficulty in range(3,0,-1):
        for planet in json_data["response"]["planets"]:
            info_data = {'id': planet["id"]}
            info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
            if info.status_code != 200:
                print("Get planet errored... trying the next planet")
                continue
            info_json = info.json()
            for zone in info_json["response"]["planets"][0]["zones"]:
                if zone["difficulty"] == difficulty and not zone["captured"] and zone["capture_progress"] < 0.9:
                    return zone["zone_position"], planet["id"], planet["state"]["name"], difficulty

        
def get_user_info():
    data = {'access_token': TOKEN}
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlayerInfo/v0001/", data=data)
    if result.status_code != 200:
        print("Getting user info errored... trying again(after 30s cooldown)")
        sleep(30)
        play_game()
    if "active_planet" in result.json()["response"]:
        return result.json()["response"]["active_planet"]
    else:
        return -1

def leave_game(current):
    data = {
        'gameid': current, 
        'access_token': TOKEN
    }  
    result = s.post("https://community.steam-api.com/IMiniGameService/LeaveGame/v0001/", data=data)
    if result.status_code != 200:
        print("Leave planet " + str(current) + " errored... trying again(after 30s cooldown)")
        sleep(30)
        play_game()

def join_planet(planet_id, planet_name):
    data = {
        'id': planet_id,
        'access_token': TOKEN
    }   
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinPlanet/v0001/", data=data)
    if result.status_code != 200:
        print("Join planet '" + str(planet_name) + "' (" + str(planet_id) + ") errored... trying again(after 30s cooldown)")
        sleep(30)
        play_game()
    else:
        print("Joined planet: " + str(planet_name) + " (" + str(planet_id) + ")")

def join_zone(zone_position):
    data = {
        'zone_position': zone_position,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Join zone " + str(zone_position) + " errored... trying again(after 1m cooldown)")
        sleep(60)
        play_game()
    else:
        print("Joined zone: " + str(result.json()["response"]["zone_info"]["zone_position"]))


def report_score(difficulty):
    data = {
        'access_token': TOKEN, 
        'score': 5*120*(2**(difficulty-1)),
        'language':'english'
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportScore/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Report score errored... trying again")
        play_game()
    else:
        print(result.json()["response"])


def play_game():
    print("Checking if user is currently on a planet")
    current = get_user_info()
    if current != -1:
        print("Leaving current planet")
        leave_game(current)
    print("Finding a planet and zone")
    zone_position, planet_id, planet_name, difficulty = get_zone()
    join_planet(planet_id, planet_name)
    while(1):
        join_zone(zone_position)
        print("Sleeping for 1 minute 50 seconds")
        sleep(110)
        report_score(difficulty)

while(1):
    try:
        play_game()
    except KeyboardInterrupt:
        print("User cancelled script")
        exit(1)
    except Exception as e:
        print(e)
        continue
