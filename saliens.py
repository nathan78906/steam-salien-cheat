import requests
import json
from time import sleep
import datetime

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""

s = requests.session()
s.headers.update({
    'User-Agent': 'steam-salien-cheat on GitHub Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://steamcommunity.com/saliengame/play/',
    'Origin': 'https://steamcommunity.com',
    'Accept': '*/*'
    })


def get_zone():
    data = {
        'active_only': 1,
        'language':'english'
    }
    result = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanets/v0001/", params=data)
    if result.status_code != 200:
        print("Get planets errored... trying again(after 10s cooldown)")
        sleep(10)
        get_zone()
    json_data = result.json()
    for difficulty in range(4, 0, -1):
        for planet in json_data["response"]["planets"]:
            info_data = {'id': planet["id"]}
            info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
            if info.status_code != 200:
                print("Get planet errored... trying the next planet")
                continue
            info_json = info.json()
            for zone in info_json["response"]["planets"][0]["zones"]:
                if zone["difficulty"] == difficulty and not zone["captured"] and zone["capture_progress"] < 0.9:
                    return str(zone["zone_position"]), planet["id"], planet["state"]["name"], difficulty


def get_user_info():
    data = {'access_token': TOKEN}
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlayerInfo/v0001/", data=data)
    if result.status_code != 200:
        print("Getting user info errored... trying again(after 10s cooldown)")
        sleep(10)
        play_game()
    if "active_zone_game" in result.json()["response"]:
        print("Stuck on zone... trying to leave")
        leave_game(result.json()["response"]["active_zone_game"])
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
        print("Leave planet {} errored... trying again(after 10s cooldown)".format(str(current)))
        sleep(10)
        play_game()


def join_planet(planet_id, planet_name):
    data = {
        'id': planet_id,
        'access_token': TOKEN
    }   
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinPlanet/v0001/", data=data)
    if result.status_code != 200:
        print("Join planet {} ({}) errored... trying again(after 10s cooldown)".format(
            str(planet_name),
            str(planet_id)))
        sleep(10)
        play_game()
    else:
        print("Joined planet: {} ({}) \n".format(
            str(planet_name),
            str(planet_id)))


def join_zone(zone_position, difficulty):
    dstr = {
        1: 'Easy',
        2: 'Medium',
        3: 'Hard',
        4: 'Boss',
    }
    data = {
        'zone_position': zone_position,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Join zone {} errored... trying again(after 10s cooldown)".format(str(zone_position)))
        sleep(10)
        play_game()
    else:
        print("Joined zone: {} (Difficulty: {})".format(
            str(zone_position),
            dstr.get(difficulty, difficulty)))


def report_score(difficulty):
    score = 600 * (2 ** (difficulty - 1))
    data = {
        'access_token': TOKEN, 
        'score': score,
        'language':'english'
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportScore/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Report score errored... Current zone likely completed...\n")
        play_game()
    else:
        res = result.json()["response"]
        score_delta = int(res["next_level_score"]) - int(res["new_score"])
        eta_seconds = int(score_delta // score) * 110
        d = datetime.timedelta(seconds=eta_seconds)
        print("Level: {} | Score: {} -> {} | Level-Up Score: {} ETA: {} {}\n".format(
            res["new_level"],
            res["old_score"],
            res["new_score"],
            res["next_level_score"],
            d,
            "Level UP!" if res["old_level"] != res["new_level"] else ""))


def play_game():
    global update_check
    print("Checking if user is currently on a planet")
    current = get_user_info()
    if current != -1:
        print("Leaving current planet")
        leave_game(current)
    print("Finding a planet and zone")
    zone_position, planet_id, planet_name, difficulty = get_zone()
    join_planet(planet_id, planet_name)
    while 1:
        join_zone(zone_position, difficulty)
        print("Sleeping for 1 minute 50 seconds")
        sleep(110)
        report_score(difficulty)
        update_check = update_check - 1
        if update_check == 0:
            print("Checking for any new planets......")
            update_check = 7
            play_game()
        get_user_info() # get user info and leave game, incase user gets stuck


while 1:
    try:
        update_check = 7
        play_game()
    except KeyboardInterrupt:
        print("User cancelled script")
        exit(1)
    except Exception as e:
        print(e)
        continue