# LinneB logging script

If you're looking for a way to log your channel in an sql database, I wouldn't use this. It's pretty slow and you need alot of stuff for it to work. I just decided to make it open-source.

---
In case you want to run it yourself, there's some stuff you need to change.
In the top of the main.py file you'll see some variables:

| Variable | Description |
| ----------- | ----------- |
| nickname | Username of the twitch account you want to use |
| token | TMI access token, you can get one [here](https://twitchapps.com/tmi/) | 
| channel | Twitch channel you want to log (with a # in the beginning) | 
| apptoken | You will need an app token for the online/offline status, you can read about them [here](https://dev.twitch.tv/docs/authentication/#app-access-tokens) | 
| clientID | ClientID that goes with the app token | 

---
You will also need a mysql server, with a table with the following format:

| Field | Description | 
| ----------- | ----------- |
| ID | Incrementing ID number | 
| date_time | Timestamp | 
| channel_live | Online/offline status of the channel at the time of the message | 
| username | Username | 
| message | Message | 

You will probably also need to install the `mysql-connector-python` python module using pip
