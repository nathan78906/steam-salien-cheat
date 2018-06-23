import requests
import json
from time import sleep

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""
SCORES_BY_DIFFICULTY = [None, 600, 1200, 2400]

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
    candidates = []
    for planet in json_data["response"]["planets"]:
        info_data = {'id': planet["id"]}
        info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
        if info.status_code != 200:
            print("Get planet errored... trying the next planet")
            continue
        info_json = info.json()
        for zone in info_json["response"]["planets"][0]["zones"]:
            if not zone["captured"] and zone["capture_progress"] < 0.9:
                candidates.append((zone["difficulty"], zone["zone_position"], planet["id"]))
    return sorted(candidates, reverse = True)[0]
        
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

def join_planet(planet):
    data = {
        'id': planet, 
        'access_token': TOKEN
    }   
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinPlanet/v0001/", data=data)
    if result.status_code != 200:
        print("Join planet " + str(planet) + " errored... trying again(after 1 minute cooldown)")
        sleep(60)
        play_game()
    else:
        print("Joined planet: " + str(planet))

def join_zone(zone):
    data = {
        'zone_position': zone,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Join zone " + str(zone) + " errored... trying again(after 30s cooldown)")
        sleep(30)
        play_game()
    else:
        print("Joined zone: " + str(result.json()["response"]["zone_info"]["zone_position"]))


def report_score(difficulty = 3):
    data = {
        'access_token': TOKEN, 
        'score': SCORES_BY_DIFFICULTY[difficulty], 
        'language':'english'
    }
    if data['score'] is None:
        raise Exception('Zero difficulty is invalid');
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
    difficulty, zone, planet = get_zone()
    join_planet(planet)
    while(1):
        join_zone(zone)
        print("Sleeping for 1 minute 50 seconds")
        sleep(110)
        report_score(difficulty)

while(1):
    try:
        play_game()
    except KeyboardInterrupt:
        print("User cancelled script");
        exit(1)
    except Exception as e:
        print e
        continue
