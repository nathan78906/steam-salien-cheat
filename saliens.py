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

def join_zone():
    data = {
        'zone_position':'34',
        'access_token':TOKEN
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/", data=data)
    if result.status_code != 200:
        print("Join zone errored... trying again")
        join_zone()
    if result.json() == {'response':{}}:
        print("Join zone failed... trying again")
        join_zone()
    print("Joined zone: " + str(result.json()["response"]["zone_info"]["zone_position"]))

def report_score():
    data = {
        'access_token':TOKEN, 
        'score': MAX_SCORE, 
        'language':'english'
    }
    result = s.post("https://community.steam-api.com/ITerritoryControlMinigameService/ReportScore/v0001/", data=data)
    if result.status_code != 200:
        print("Report score errored... trying again")
        report_score()
    if result.json() == {'response':{}}:
        print("Report score failed... trying again")
        report_score()
    print(result.json()["response"])


while(1):
    join_zone()
    print("Sleeping for 1 minute 50 seconds")
    sleep(110)
    report_score()
