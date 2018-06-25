import requests
import json
from time import sleep
import logging

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""

s = requests.session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://steamcommunity.com/saliengame/play/',
    'Origin': 'https://steamcommunity.com',
    'Accept': '*/*'
    })

# config logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# config logging for requests to WARNING
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.WARNING)
requests_log.propagate = True


def get_zone():
    data = {'active_only': 1}
    result = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanets/v0001/", params=data)
    if result.status_code != 200:
        logging.warning("Get planets errored... trying again(after 10s cooldown)")
        sleep(10)
        get_zone()
    json_data = result.json()
    for difficulty in range(4, 0, -1):
        for planet in json_data["response"]["planets"]:
            info_data = {'id': planet["id"]}
            info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
            if info.status_code != 200:
                logging.warning("Get planet errored... trying the next planet")
                continue
            info_json = info.json()
            for zone in info_json["response"]["planets"][0]["zones"]:
                if zone["difficulty"] == difficulty and not zone["captured"] and zone["capture_progress"] < 0.9:
                    return zone["zone_position"], planet["id"], planet["state"]["name"], difficulty


def get_user_info():
    data = {'access_token': TOKEN}
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlayerInfo/v0001/", data=data)
    if result.status_code != 200:
        logging.warning("Getting user info errored... trying again(after 10s cooldown)")
        sleep(10)
        play_game()
    if "active_zone_game" in result.json()["response"]:
        logging.debug("Stuck on zone... trying to leave")
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
        logging.warning("Leave planet " + str(current) + " errored... trying again(after 10s cooldown)")
        sleep(10)
        play_game()


def join_planet(planet_id, planet_name):
    data = {
        'id': planet_id,
        'access_token': TOKEN
    }   
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinPlanet/v0001/", data=data)
    if result.status_code != 200:
        logging.warning("Join planet " + str(planet_id) + " errored... trying again(after 10s cooldown)")
        sleep(10)
        play_game()
    else:
        logging.debug("Joined planet: " + str(planet_id))


def join_zone(zone_position, difficulty):
    data = {
        'zone_position': zone_position,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        logging.warning("Join zone " + str(zone_position) + " errored... trying again(after 1m cooldown)")
        sleep(60)
        play_game()
    else:
        logging.debug("Joined zone: " + str(zone_position) + " (Difficulty: " + str(difficulty) + ")")


def report_score(difficulty):
    data = {
        'access_token': TOKEN, 
        'score': 5*120*(2**(difficulty-1)),
        'language':'english'
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportScore/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        logging.warning("Report score errored... Current zone likely completed...\n")
        play_game()
    else:
        res = result.json()["response"]
        logging.debug("Old Score: " + str(res["old_score"]) + " (Level " + str(res["old_level"]) + ") - " + "New Score: " + str(res["new_score"]) + " (Level " + str(res["new_level"]) + ") - " + "Next Level Score: " + str(res["next_level_score"]) + "\n")


def play_game():
    global update_check
    logging.debug("Checking if user is currently on a planet")
    current = get_user_info()
    if current != -1:
        logging.debug("Leaving current planet")
        leave_game(current)
    logging.debug("Finding a planet and zone")
    zone_position, planet_id, planet_name, difficulty = get_zone()
    join_planet(planet_id, planet_name)
    while 1:
        join_zone(zone_position, difficulty)
        logging.debug("Sleeping for 1 minute 50 seconds")
        sleep(110)
        report_score(difficulty)
        update_check = update_check - 1
        if update_check == 0:
            logging.debug("Checking for any new planets......")
            update_check = 7
            play_game()


while 1:
    try:
        update_check = 7
        play_game()
    except KeyboardInterrupt:
        logging.debug("User cancelled script")
        exit(1)
    except Exception as e:
        logging.exception(e)
        continue
