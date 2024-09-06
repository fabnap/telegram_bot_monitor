# SIDDHARTA-2 telegram bot
### made by Fabrizio Napolitano 
### Laboratori Nazionali di Frascati - INFN

## What is this repository for?
This is the legacy of the telegram bot of the SIDDHARTA-2 nuclear experiment at the Frascati National Laboratory. 

Over the last years, I've built this project to help monitor the experiment and to provide a simple way to check the status of the experiment. The bot is able to send messages to a telegram group, to a single user, and to send images and plots. The bot is also able to receive commands from the users and to send the data to a database. The bot is written in Python and uses the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library. The bot is running on a dedicated server, and it is connected to the experiment network. 
Tests are available to check the bot functionalities.
It was a great experience to build this project and to see it working, and it was used by shifters and experts over the operation lifetime of the experiment.
I am now sharing this project, hoping that it can a useful start for similar projects, even though many features are really unique to the SIDDHARTA-2 experiment, it is fairly easily customizable.

## Philosophy of the project
The data acquisition (DAQ) systems of the experiment are running on dedicated servers, and data from all sensors and performances are output to log files, so called *push* (the actual data is produced in binary form and stored separately), but I think it could be easily adapted to different (maybe more appropriate) databases.
Additionally, the accelerator complex, DaΦne, is also producing log files with the status of the machine and the beam.

This telegram bot works as follows: 
- Every `self.interval` seconds of the class `siddharta2_bot`, all the logs are read and the data is processed.
- Additional checks are performed (such as ping other servers) monitor the status of the experiment.
- The conditions are checked, and counters are updated if conditions meet the requirements, categorized in WARNING ⚠️, ERROR, and CRITICAL ❌. Here WARNING is a minor issue, which can be e.g. solved the following morning if e.g. happening over the night, but requiring checks, ERROR is a major issue which should be addressed immediately, and CRITICAL is a severe issue which require attention of all people available since the data taking and/or the experimental apparatus itself could be in danger.
- When a threshold is reached, the bot sends a message to the telegram group as long as the condition is met, informing the shifters and experts about the issue, and suggesting further actions.
    - The shifter acknowledges the message by masking it with `/mask`, and the bot stops sending messages.
- If the issue is a warning, the messages are suppressed after few minutes, to avoid spamming.
- The bot is also able to send images and plots, and to receive commands from the users, which are available in with the `/help` command.

## Specific features

- `check_dafne_push` is responsible to check the status of the DaΦne accelerator complex, and to send a message if the status is not nominal, or not matching with experimental data.
- `check_slowcontrol_push` The slow control concerns the status of the experimental apparatus, such as the temperature of the detectors, the pressure of the gas, the status of the cooling system, etc. The nominal values are stored as a json file, and the bot compares the values with the experimental data. New defaults can be set with the `/setalarms` command.
- `check_lumi_push` The monitor of the luminosity detector, a separate detector which is used to monitor the luminosity of the beam.
- `check_sdd_push` the Silicon Drift Detectors (SDDs) are the heart of the experiment, and the status of the SDDs is crucial for the data taking. Here their rates is monitored and compared to the experimental status.
- `check_global` check global conditions, e.g. if there is beam there should be rates on the SDDs and luminosity detector.
- `check_czt_global` check the status of the Cadmium-Zinc-Telluride (CZT) detectors, which are used as a satellite detector system.
- `check_pings` check the status of the servers, and if they are reachable.

## Tests 
I tried to cover all the important cases of relevance for us in the `test_main.py` file. The tests are written with the `unittest` library, and they are run with the `python3 test_main.py` command. The tests are covering the main functionalities of the bot, such as the sending of messages, the sending of images, the sending of plots, the receiving of commands, the acknowledgment of messages, the suppression of messages, the setting of alarms, the reading of logs, the processing of logs, the checking of conditions, the updating of counters, the sending of messages when conditions are met, the stopping of messages when conditions are not met, the sending of messages when conditions are met again, the sending of messages when conditions are met again after the acknowledgment, the sending of messages when conditions are met again after the suppression.

## How to start telegram bot

Just start it with the `python3 main.py` command, and the bot will start running.
If you want to make it a systemctl service, you can add the following service file in `/etc/systemd/system/telegramMain.service`:

```
[Unit]
Description=telegramMain
OnFailure=telegram-on-failure.target
[Service]
ExecStart=/usr/bin/python3 main.py
WorkingDirectory=/your/path/to/the/bot
User=youruser
Group=yourgroup
Restart=always


[Install]
WantedBy=multi-user.target
```
and start with `sudo systemctl star telegramMain`

The bot will start running, and you can interact with it with the telegram app.
To do so, you need to create a new bot with the [BotFather](https://core.telegram.org/bots#6-botfather), and to get the token.
Then you can start the bot with the token, and you can interact with it. Remember to add the bot to a group, and to give the bot the permission to write messages in the group. Also remember to add the bot id to the `self.token` variable in the `siddharta2_bot` class. 
Then you can simply start the bot with `/start` and you can interact with it with the commands available in the `/help` command.

## Note
Do not hesitate to contact me in case of questions