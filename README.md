# steam-salien-cheat
Simulates the playing of the "Summer Saliens" game on steam. Automatically chooses a planet/zone that will give you the max exp. Will switch between planets/zones once they're completed.

#### Updates:
- Added ETA for next level
- Added a check to see if users were stuck in a zone, should reduce the amount of "Join Zone" errors
- Cleaned up the UI, doesn't output any JSON now
- Added boss zone support, no one knows the max score for boss zones yet, so it's been set to 4800 (from the same calculations used for low/medium/high) - Will probably by updated once they're actually released
- Checks for new planets every **14** minutes, this will reduce the amount of errors encountered by being in a zone and it getting 100% captured before you are able to submit your score
	- The time check can be modified by changing the `update_check` variable

## Steps
1. Visit https://steamcommunity.com/saliengame/gettoken when logged in and get the `token` value
2. Enter the `token` on `line 6` in `saliens.py`
3. Open a command line/terminal and run the program as `python saliens.py`

#### Note:
- You need to have python installed
- You need to run `pip install requests` to get the requests module, before you can run the script

### Join Zone Error?
- Stop the script, wait 2 minutes, then re-run 
- OR, leave the script running and wait for the 2 minute cooldown to finish

### Screenshot
![Screenshot](https://raw.githubusercontent.com/nathan78906/steam-salien-cheat/master/screenshot.png)
