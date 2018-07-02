# steam-salien-cheat
Simulates the playing of the "Summer Saliens" game on steam. Automatically chooses a planet/zone that will give you the max exp. Will switch between planets/zones once they're completed.

#### Updates:
- **BOSS ZONE SUPPORT**
- **Extra steps required for personalized boss output (OPTIONAL, see step 3)**
- Now checks for new zones after every game played
- Added ETA for next level

## Steps
1. Visit https://steamcommunity.com/saliengame/gettoken when logged in and get the `token` value and `steamid` value
2. Enter the `token` on `line 7` in `saliens.py`
3. Enter the `steamid` on `line 8` in `saliens.py`
4. Open a command line/terminal and run the program as `python saliens.py`

#### Note:
- You need to have python installed
- You need to run `pip install requests` to get the requests module, before you can run the script

### Join Zone Error?
- Stop the script, wait 2 minutes, then re-run 
- OR, leave the script running and wait for the 2 minute cooldown to finish

### Screenshots
Normal Zones

![Screenshot](https://raw.githubusercontent.com/nathan78906/steam-salien-cheat/master/screenshot.png)

Boss Zones

![Screenshot](https://raw.githubusercontent.com/nathan78906/steam-salien-cheat/master/screenshot-boss.png)
