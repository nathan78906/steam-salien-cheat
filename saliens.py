import requests
import json
from time import sleep
import datetime

# Get from: https://steamcommunity.com/saliengame/gettoken
TOKEN = ""
STEAMID = ""


s = requests.session()
s.headers.update({
    'User-Agent': 'steam-salien-cheat on GitHub Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://steamcommunity.com/saliengame/play/',
    'Origin': 'https://steamcommunity.com',
    'Accept': '*/*'
    })


def steam64_to_steam3(commid):
    if commid == "":
        return commid
    steamid64ident = 76561197960265728
    steamidacct = int(commid) - steamid64ident
    return steamidacct


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
    valid = []
    # check for boss zone TODO: find better way for this
    for planet in json_data["response"]["planets"]:
        info_data = {'id': planet["id"]}
        info = s.get("https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/", params=info_data)
        if info.status_code != 200:
            print("Get planet errored... trying the next planet")
            continue
        info_json = info.json()
        for zone in info_json["response"]["planets"][0]["zones"]:
            if not zone["captured"]:
                if zone["type"] == 4 and zone["boss_active"] and not zone["captured"]:
                    valid += [(zone["type"], zone["zone_position"], zone["difficulty"], planet["id"], planet["state"]["name"], True)]
                if zone["type"] == 3 and "capture_progress" in zone and zone["capture_progress"] < 0.9 and zone["capture_progress"] != 0:
                    valid += [(zone["type"], zone["zone_position"], zone["difficulty"], planet["id"], planet["state"]["name"],  False)]
    return sorted(valid, key = lambda x: (x[0], x[2]), reverse=True)[0]


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
    if "active_boss_game" in result.json()["response"]:
        print("Stuck on boss zone... trying to leave")
        leave_game(result.json()["response"]["active_boss_game"])
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
        3: 'Hard'
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
        if "next_level_score" not in res:
            print("Level: {} | Score: {} -> {}".format(
                res["new_level"],
                res["old_score"],
                res["new_score"]))
        else:
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


def play_boss(zone_position):
    data = {
        'zone_position': zone_position,
        'access_token': TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinBossZone/v0001/", data=data)
    if result.status_code != 200 or result.json() == {'response':{}}:
        print("Join boss zone {} errored... trying again(after 10s cooldown)".format(str(zone_position)))
        sleep(10)
        play_game()
    else:
        heal = 24
        max_retries = 3
        print("Joined boss zone: {}".format(str(zone_position)))
        while 1:
            sleep(5)
            if heal == 0:
                use_heal = 1
                heal = 24
            else:
                use_heal = 0
            damage_data = {
                'access_token': TOKEN,
                'use_heal_ability': use_heal,
                'damage_to_boss': 1,
                'damage_taken': 0
            }   
            result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportBossDamage/v0001/", data=damage_data)
            if result.status_code != 200 or result.json() == {'response':{}}:
                print("Report boss score errored... retrying")              
                if max_retries == 0:
                    break   
                max_retries = max_retries - 1
                continue
            res = result.json()["response"]
            if res["waiting_for_players"]:
                continue
            if res["game_over"]:
                break
            print("Boss HP: {}/{} | Lasers: {} | Team Heals: {}\n".format(
                res["boss_status"]["boss_hp"],
                res["boss_status"]["boss_max_hp"],
                res["num_laser_uses"],
                res["num_team_heals"]))
            for player in res["boss_status"]["boss_players"]:
                STEAM3ID = steam64_to_steam3(STEAMID)
                if player["accountid"] == STEAM3ID or STEAM3ID == "":
                    print("Name: {} | HP: {}/{} | XP Earned: {}".format(
                        player["name"],
                        player["hp"],
                        player["max_hp"],
                        player["xp_earned"]))
            heal = heal - 1

def play_game():
    print("Checking if user is currently on a planet")
    current = get_user_info()
    if current != -1:
        print("Leaving current planet")
        leave_game(current)
    while 1:
        print("Finding a planet and zone")
        zone_type, zone_position, difficulty, planet_id, planet_name, boss = get_zone()
        join_planet(planet_id, planet_name)
        if boss:
            play_boss(zone_position)
        else:
            join_zone(zone_position, difficulty)
            print("Sleeping for 1 minute 50 seconds")
            sleep(110)
            report_score(difficulty)
        get_user_info() # get user info and leave game, incase user gets stuck


while 1:
    try:
        play_game()
    except KeyboardInterrupt:
        print("User cancelled script")
        exit(1)
    except Exception as e:
        print(e)
        continue
