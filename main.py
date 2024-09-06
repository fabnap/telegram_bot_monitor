from telegram.ext import Updater,CommandHandler 
from telegram.ext import MessageHandler,Filters,InlineQueryHandler
import requests
import re
import os.path, time
import subprocess
import threading 
import logging
import telegram
import datetime
import signal
from functools import wraps
import sys
import json
## the boundaries for the alarms
import alarms_siddharta2 as as2

class siddharta2_bot:
    def __init__(self):
        self.token='___your_telegram_token___'
        self.bot = telegram.Bot(token=self.token)
        self.updater = Updater(self.token, use_context=True)
        # the chat ids of the allowed users
        self.allowed_chat_ids = []
        self.allowed_start_stop = []
        self.process = None
        self.TEST_MODE = False
        # self.TEST_MODE = True
        self.interval = 30 if not self.TEST_MODE else 5
        self.logger = self.setup_logger()
        self.update_file_paths()

        self.dafenerrcounter  = 0
        self.lmerrcounter  = 0
        self.sdderrcounter  = 0
        self.kaonsratecntr = 0
        self.kaonsratecntr2 = 0
        self.kaonsrateold = 0
        self.kaons_on_lumi = 0
        self.kaonserrcounter = 0
        self.kaonserrcounter2 = 0
        self.slctrokerrcounter  = 0
        self.beamdowncounter = 0
        self.slctrpressurecounter = 0
        self.slctrpressurecounter2 = 0
        self.slctrpressurevacuum = 0
        self.slctrpressurevacuum2 = 0
        self.slctrtemperatures = 0
        self.slctrtemperatures2 = 0
        self.cztcounter = 0
        self.maskPressure = 0
        self.maskVacuum = 0
        self.maskTemperature = 0
        self.maskGlobalStatus = 0
        self.maskCZT = 0
        self.maskPings = 0
        self.dafneok = False
        self.beamin  = False
        self.lmok    = False
        self.sddok   = False
        self.slctrok = False
        self.as2 = self.get_updated_values()
        self.is_started = False
        self.logger.info("BOT INITIALIZED")

    def get_updated_values(self):
        with open('alarms_siddharta2.json', 'r') as f:
            data = json.load(f)
        return data

    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C or received a SIGTERM!')
        if self.process:
            # process.terminate()
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)  # Send the signal to all the process in the group
        sys.exit(0)

        
    def setup_logger(self):
        logging.basicConfig(filename='tmain.log', level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        return logger

    def update_file_paths(self):
        now = datetime.datetime.now()
        year = '{:02d}'.format(now.year)
        month = '{:02d}'.format(now.month)
        day = '{:02d}'.format(now.day)

        if not self.TEST_MODE:
            self.filenameslowcontrol = "/media/logssid2/sdd_single_log.txt"
            self.filenamedafne = "/media/dataFromDafne/" + year + month + day + ".stat"
            self.filenamesidd = "/media/dataFromSiddharta/" + year + month + day + "_siddharta.dat"
            self.filenamesiddsdd = "/media/dataFromSiddharta/" + year + month + day + "_sdd_siddharta.dat"
            self.filenameoldsiddharta = "/media/dataFromSiddharta/old_siddharta.stat"

        else:
            self.filenameslowcontrol = "testslowcontrol.txt"
            self.filenamedafne = "testsdafne.txt"
            self.filenamesidd = "testslumi.txt"
            self.filenamesiddsdd = "testssidd.txt"
            self.filenametest = "testpush.txt"
            self.filenameoldsiddharta = "test_oldsiddharta.txt"

    # python decorator
    def restricted(func):
        @wraps(func)
        def wrapped(self, update, context, *args, **kwargs):
            chat_id = update.effective_chat.id
            if chat_id not in self.allowed_chat_ids:
                return  # Ignore command
            return func(self, update, context, *args, **kwargs)
        return wrapped

    def restricted_start(func):
        @wraps(func)
        def wrapped(self, update, context, *args, **kwargs):
            chat_id = update.effective_chat.id
            if chat_id not in self.allowed_start_stop:
                return  # Ignore command
            return func(self, update, context, *args, **kwargs)
        return wrapped
    
    def send_message(self, update, context, message):
        if self.TEST_MODE:
            logging.info(message)
        else:
            if update is not None:
                context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode= 'Markdown')
            else:
                context.bot.send_message(chat_id=context.job.context, text=message, parse_mode= 'Markdown')


    @restricted
    def help_command(self, update, context):
        help_text = """
        Here are the commands you can use:
        /help - Show this help message
        /start - Start the bot
        /restart - Restart the bot
        /stop - Stop the bot
        /snap - Snap current, Slowcotrol, SDD rates 
        /snapsl - Snap slow control command
        /emergencyrestart - Emergency restart command. Restart services on usersdd which are down
        /masks - Present mask options
        /maskPressure - Mask pressure options
        /maskVacuum - Mask vacuum options
        /maskTemperature - Mask temperature options
        /maskGlobalStatus - Mask global status options
        /maskCZT - Mask CZT checker options
        /maskPings - Mask pings options
        /unMaskPressure - Unmask pressure options
        /unMaskVacuum - Unmask vacuum options
        /unMaskTemperature - Unmask temperature options
        /unMaskGlobalStatus - Unmask global status options
        /unMaskCZT - Unmask CZT checker options
        /unMaskPings - Unmask pings options
        /unMaskAll - Unmask all options
        /setalarms - Set the alarm values to present ones
        /start\_cztchecker - Start cztchecker process
        /stop\_cztchecker - Stop cztchecker process
        """

        self.send_message(update, context, help_text)
		
    def ping(self, host):

        param = '-c'
        timeout = '-W'
        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', timeout, '15', host] # 15 seconds timeout
        return subprocess.call(command) == 0

    @restricted
    def start_cztchecker(self, update, context):

        # Check if the process is already running
        if self.process is not None and self.process.poll() is None:
            self.send_message(update, context, "cztchecker.sh is already running")

        else:
            self.process = subprocess.Popen(["bash", "cztchecker.sh"], preexec_fn=os.setsid)
            self.send_message(update, context, "cztchecker.sh is started")

    @restricted
    def stop_cztchecker(self, update, context):
        # Use the global keyword to indicate that you want to use the global process variable

        if self.process:
            # process.terminate()
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)  # Send the signal to all the process in the group
            self.send_message(update, context, "cztchecker.sh is stopped")
            self.process = None
        else:
            self.send_message(update, context, "No running cztchecker.sh to stop")

    @restricted
    @restricted_start
    def start(self, update, context):
        if self.is_started:
            self.send_message(update, context, "ℹ️ *INFO* ℹ️:Already ON!")
            return
        self.logger.info("Starting...")

        # reset the counters
        self.dafenerrcounter      = 0
        self.lmerrcounter         = 0
        self.sdderrcounter        = 0
        self.kaonsratecntr		 = 0 
        self.kaonsratecntr2		 = 0 
        self.kaonsrateold		 = 0 
        self.kaonserrcounter 	 = 0
        self.kaonserrcounter2 	 = 0
        self.kaons_on_lumi 		 = 0
        self.slctrokerrcounter    = 0
        self.beamdowncounter      = 0
        self.slctrpressurecounter = 0
        self.slctrpressurecounter2= 0
        self.slctrpressurevacuum  = 0
        self.slctrpressurevacuum2 = 0
        self.slctrtemperatures	 = 0
        self.slctrtemperatures2	 = 0
        self.cztcounter          = 0 
        self.maskPressure       = False
        self.maskVacuum         = False
        self.maskTemperature    = False
        self.maskGlobalStatus   = False
        self.maskCZT            = False
        self.maskPings          = False
        self.is_started = True


        self.send_message(update, context, "ℹ️ *INFO* ℹ️:Welcome to the SIDDHARTA2 telegram updater")

        # context.job_queue.run_repeating(callback_minute, interval=10, first=30,
        self.logger.info(self.kaonserrcounter)
        # Call start_cztchecker at the end
        self.start_cztchecker(update, context)

        jb = context.job_queue.run_repeating(self.callback_minute, interval=self.interval ,context=update.message.chat_id)
        self.logger.info("Service job launched")



    @restricted
    def restart(self, update, context):

        self.send_message(update, context, "ℹ️ *INFO* ℹ️:Restarting!")
        context.job_queue.jobs()[0].enabled=True

    @restricted
    def stop(self, update, context):
        if not self.is_started:
            self.send_message(update, context, "ℹ️ *INFO* ℹ️:Already OFF!")
            return
        self.send_message(update, context, "ℹ️ *INFO* ℹ️:Stopped!")
        # print(context.job_queue.jobs() )
        context.job_queue.jobs()[0].enabled=False
        # context.job_queue.stop() # this cannot be restarted
        self.is_started = False
        self.stop_cztchecker(update, context)
        self.logger.info("Service job stopped")



    def check_dafne_push(self, context):

        now=int(time.time())
        nowtosplit = datetime.datetime.now()
        hour = '{:02d}'.format(nowtosplit.hour)

        chat_id=context.job.context

        night = False
        if (int(hour) > 23 or int(hour) < 8):
            night = True

        try:
            linedafne = subprocess.run(['tail', '-1', self.filenamedafne], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            timedafne=int(linedafne.split(" ")[0])
            # print(timedafne)
            self.logger.info(timedafne)
            if(now - timedafne > 700):
                if self.dafenerrcounter < 10:
                    self.dafenerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAFNE push not updating")
                if self.dafenerrcounter == 10:
                    self.dafenerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAFNE push not updating - suppressing")

            else:
                if self.dafenerrcounter > 5:

                    self.send_message( None, context, "ℹ️ *INFO* ℹ️: DAFNE push back online")

                self.dafenerrcounter = 0
                self.dafneok=True
            
                # print("currents")
                ip=float(linedafne.split(" ")[1])
                ie=float(linedafne.split(" ")[2])
                # print (ip,ie)
                if(ip > 20. and ie > 20.):
                    self.beamin=True
                    self.beamdowncounter = 0
                if(ip < 5. and ie < 5.):
                    self.beamdowncounter+=1
                    if(self.beamdowncounter == 2 and not night ):
                        self.send_message(None, context, "ℹ️ *INFO* ℹ️: DAFNE beam down")

        except Exception as e:
            # logging.error(f"Error executing tail command: {e.stderr.decode('utf-8')}")
            logging.error(f"An error occurred: {str(e)}")

            timedafne=0
            if self.dafenerrcounter < 10:
                self.dafenerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAFNE push not present")
            if self.dafenerrcounter == 10:
                self.dafenerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAFNE push not present - suppressing")   


    def check_slowcontrol_push(self, context):
        now=int(time.time())
        chat_id=context.job.context

        try:
            slowcontrollastupdate=int(os.path.getmtime(self.filenameslowcontrol))
            if(now - slowcontrollastupdate > 350):
                if self.slctrokerrcounter < 10:
                    self.slctrokerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: Slow Control not updating")
                if self.slctrokerrcounter == 10:
                    self.slctrokerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: Slow Control not updating - suppressing")
            else:
                if self.slctrokerrcounter > 5:
                    self.send_message(None, context, "ℹ️ *INFO* ℹ️: Slow Control back online")
                self.slctrokerrcounter = 0
                self.slctrok=True


            # --- SLOW CRL PRESSURE TGT--- #
            lineslowcontrol = subprocess.run(['tail', '-1', self.filenameslowcontrol], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            pressureTarget=float(lineslowcontrol.split("\t")[13])
            vaccumPressure=float(lineslowcontrol.split("\t")[14])
            tsdd1=float(lineslowcontrol.split("\t")[1])
            tsdd2=float(lineslowcontrol.split("\t")[2])
            tsdd3=float(lineslowcontrol.split("\t")[3])
            tsdd4=float(lineslowcontrol.split("\t")[4])
            tsdd5=float(lineslowcontrol.split("\t")[5])
            tsdd6=float(lineslowcontrol.split("\t")[6])
            tsdda=float(lineslowcontrol.split("\t")[7])
            tsddb=float(lineslowcontrol.split("\t")[8])
            tsddc=float(lineslowcontrol.split("\t")[9])
            tsddd=float(lineslowcontrol.split("\t")[10])
            tsdr1=float(lineslowcontrol.split("\t")[16])
            tsdr2=float(lineslowcontrol.split("\t")[18])
            # print(pressureTarget,vaccumPressure,tsdd1,tsdd2,tsdd3,tsdd4,tsdd5,tsdd6,tsdda,tsddb,tsddc,tsddd,tsdr1,tsdr2)
            # print(self.as2["alarms_dict"]["pressure"][2])
            if not self.maskPressure:
                if (pressureTarget > self.as2["alarms_dict"]["pressure"][2]):
                    if self.slctrpressurecounter < 10:
                        self.slctrpressurecounter+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: PRESSURE TARGET HIGH")
                    if self.slctrpressurecounter == 10:
                        self.slctrpressurecounter+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: PRESSURE TARGET HIGH - suppressing - action is required")

                    if (pressureTarget > self.as2["alarms_dict"]["pressure"][3]):
                        if self.slctrpressurecounter2 < 10:
                            self.slctrpressurecounter2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: PRESSURE TARGET HIGH - gas will be released.")
                        if self.slctrpressurecounter2 == 10:
                            # self.slctrpressurecounter2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: PRESSURE TARGET HIGH - not suppressing - ACTION IS REQUIRED IMMEDIATELY")
                if (pressureTarget < self.as2["alarms_dict"]["pressure"][1]):
                    if self.slctrpressurecounter < 10:
                        self.slctrpressurecounter+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: PRESSURE TARGET LOW")
                    if self.slctrpressurecounter == 10:
                        self.slctrpressurecounter+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: PRESSURE TARGET LOW - suppressing - action is required")

                    if (pressureTarget < self.as2["alarms_dict"]["pressure"][0]):
                        if self.slctrpressurecounter2 < 10:
                            self.slctrpressurecounter2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: PRESSURE TARGET LOW")
                        if self.slctrpressurecounter2 == 10:
                            # self.slctrpressurecounter2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: PRESSURE TARGET LOW - not suppressing - ACTION IS REQUIRED IMMEDIATELY")



                if (pressureTarget < self.as2["alarms_dict"]["pressure"][3] and pressureTarget > self.as2["alarms_dict"]["pressure"][1]):
                    if self.slctrpressurecounter > 5:
                        self.send_message(None, context, "ℹ️ *INFO* ℹ️: PRESSURE TARGET again in range")  
                    self.slctrpressurecounter=0
                    self.slctrpressurecounter2=0
            
            ##############################################				
            if not self.maskVacuum:
                if (vaccumPressure > self.as2["alarms_dict"]["vacuum"][2]):
                    if self.slctrpressurevacuum < 10:
                        self.slctrpressurevacuum+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: VACUUM PRESSURE > 5e-6 mbar")
                    if self.slctrpressurevacuum == 10:
                        self.slctrpressurevacuum+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: VACUUM PRESSURE > 5e-6 mbar - suppressing - action is required")

                    if (vaccumPressure > self.as2["alarms_dict"]["vacuum"][3]):
                        if self.slctrpressurevacuum2 < 10:
                            self.slctrpressurevacuum2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: VACUUM PRESSURE > 1e-5 mbar - LOOSING THE VACUUM - SDDs IN DANGER IF ON.")
                        if self.slctrpressurevacuum2 == 10:
                            # self.slctrpressurevacuum2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: VACUUM PRESSURE > 1e-5 mbar - not suppressing - ACTION IS REQUIRED IMMEDIATELY")

                if (vaccumPressure < self.as2["alarms_dict"]["vacuum"][2] ):
                    if self.slctrpressurevacuum > 5:
                        self.send_message(None, context, "ℹ️ *INFO* ℹ️: VACUUM PRESSURE again in range")
                    self.slctrpressurevacuum=0
                    self.slctrpressurevacuum2=0



            if not self.maskTemperature:
                if (tsdd1 > self.as2["alarms_dict"]["tsdd1"][2] or tsdd2 > self.as2["alarms_dict"]["tsdd2"][2] or tsdd3 > self.as2["alarms_dict"]["tsdd3"][2] or tsdd4 > self.as2["alarms_dict"]["tsdd4"][2] or tsdd5 > self.as2["alarms_dict"]["tsdd5"][2] or tsdd6 > self.as2["alarms_dict"]["tsdd6"][2] or tsdda > self.as2["alarms_dict"]["tsdda"][2] or tsddb > self.as2["alarms_dict"]["tsddb"][2] or tsddc > self.as2["alarms_dict"]["tsddc"][2] or tsddd > self.as2["alarms_dict"]["tsddd"][2] or tsdr1 > self.as2["alarms_dict"]["tsdr1"][2] or tsdr2 > self.as2["alarms_dict"]["tsdr2"][2]):
                    if self.slctrtemperatures < 10:
                        self.slctrtemperatures+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: TEMPERATURES out of range.")
                    if self.slctrtemperatures == 10:
                        self.slctrtemperatures+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: TEMPERATURES out of range - suppressing.")
                    if (tsdd1 > self.as2["alarms_dict"]["tsdd1"][3] or tsdd2 > self.as2["alarms_dict"]["tsdd2"][3] or tsdd3 > self.as2["alarms_dict"]["tsdd3"][3] or tsdd4 > self.as2["alarms_dict"]["tsdd4"][3] or tsdd5 > self.as2["alarms_dict"]["tsdd5"][3] or tsdd6 > self.as2["alarms_dict"]["tsdd6"][3] or tsdda > self.as2["alarms_dict"]["tsdda"][3] or tsddb > self.as2["alarms_dict"]["tsddb"][3] or tsddc > self.as2["alarms_dict"]["tsddc"][3] or tsddd > self.as2["alarms_dict"]["tsddd"][3] or tsdr1 > self.as2["alarms_dict"]["tsdr1"][3] or tsdr2 > self.as2["alarms_dict"]["tsdr2"][3]):
                        if self.slctrtemperatures2 < 10:
                            self.slctrtemperatures2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY.")
                        if self.slctrtemperatures2 == 10:
                            # self.slctrtemperatures2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")


                if (tsdd1 < self.as2["alarms_dict"]["tsdd1"][1] or tsdd2 < self.as2["alarms_dict"]["tsdd2"][1] or tsdd3 < self.as2["alarms_dict"]["tsdd3"][1] or tsdd4 < self.as2["alarms_dict"]["tsdd4"][1] or tsdd5 < self.as2["alarms_dict"]["tsdd5"][1] or tsdd6 < self.as2["alarms_dict"]["tsdd6"][1] or tsdda < self.as2["alarms_dict"]["tsdda"][1] or tsddb < self.as2["alarms_dict"]["tsddb"][1] or tsddc < self.as2["alarms_dict"]["tsddc"][1] or tsddd < self.as2["alarms_dict"]["tsddd"][1] or tsdr1 < self.as2["alarms_dict"]["tsdr1"][1] or tsdr2 < self.as2["alarms_dict"]["tsdr2"][1]):
                    if self.slctrtemperatures < 10:
                        self.slctrtemperatures+=1
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: TEMPERATURES out of range.")
                    if self.slctrtemperatures == 10:
                        self.slctrtemperatures+=1

                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: TEMPERATURES out of range - suppressing.")
                    if (tsdd1 < self.as2["alarms_dict"]["tsdd1"][0] or tsdd2 < self.as2["alarms_dict"]["tsdd2"][0] or tsdd3 < self.as2["alarms_dict"]["tsdd3"][0] or tsdd4 < self.as2["alarms_dict"]["tsdd4"][0] or tsdd5 < self.as2["alarms_dict"]["tsdd5"][0] or tsdd6 < self.as2["alarms_dict"]["tsdd6"][0] or tsdda < self.as2["alarms_dict"]["tsdda"][0] or tsddb < self.as2["alarms_dict"]["tsddb"][0] or tsddc < self.as2["alarms_dict"]["tsddc"][0] or tsddd < self.as2["alarms_dict"]["tsddd"][0] or tsdr1 < self.as2["alarms_dict"]["tsdr1"][0] or tsdr2 < self.as2["alarms_dict"]["tsdr2"][0]):
                        if self.slctrtemperatures2 < 10:
                            self.slctrtemperatures2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY.")
                        if self.slctrtemperatures2 == 10:                            # self.slctrtemperatures2+=1
                            self.send_message(None, context, "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")


                if (tsdd1 < self.as2["alarms_dict"]["tsdd1"][2] and tsdd2 < self.as2["alarms_dict"]["tsdd2"][2] and tsdd3 < self.as2["alarms_dict"]["tsdd3"][2] and tsdd4 < self.as2["alarms_dict"]["tsdd4"][2] and tsdd5 < self.as2["alarms_dict"]["tsdd5"][2] and tsdd6 < self.as2["alarms_dict"]["tsdd6"][2] and tsdda < self.as2["alarms_dict"]["tsdda"][2] and tsddb < self.as2["alarms_dict"]["tsddb"][2] and tsddc < self.as2["alarms_dict"]["tsddc"][2] and tsddd < self.as2["alarms_dict"]["tsddd"][2] and tsdr1 < self.as2["alarms_dict"]["tsdr1"][2] and tsdr2 < self.as2["alarms_dict"]["tsdr2"][2])       and           (tsdd1 > self.as2["alarms_dict"]["tsdd1"][1] and tsdd2 > self.as2["alarms_dict"]["tsdd2"][1] and tsdd3 > self.as2["alarms_dict"]["tsdd3"][1] and tsdd4 > self.as2["alarms_dict"]["tsdd4"][1] and tsdd5 > self.as2["alarms_dict"]["tsdd5"][1] and tsdd6 > self.as2["alarms_dict"]["tsdd6"][1] and tsdda > self.as2["alarms_dict"]["tsdda"][1] and tsddb > self.as2["alarms_dict"]["tsddb"][1] and tsddc > self.as2["alarms_dict"]["tsddc"][1] and tsddd > self.as2["alarms_dict"]["tsddd"][1] and tsdr1 > self.as2["alarms_dict"]["tsdr1"][1] and tsdr2 > self.as2["alarms_dict"]["tsdr2"][1]):
                    if self.slctrtemperatures > 5:
                        self.send_message(None, context, "ℹ️ *INFO* ℹ️: TEMPERATURES again in range")
                    self.slctrtemperatures=0
                    self.slctrtemperatures2=0
        except Exception as e:
            # logging.error(f"Error executing tail command: {e.stderr.decode('utf-8')}")
            logging.error(f"An error occurred: {str(e)}")

            # print("there was an exception")
            slowcontrollastupdate=0
            if self.slctrokerrcounter < 10:
                self.slctrokerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error")
            if self.slctrokerrcounter == 10:
                self.slctrokerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error - suppressing")

    def check_lumi_push(self, context):
        chat_id=context.job.context
        now=int(time.time())
        try:
            linesidd = subprocess.run(['tail', '-1', self.filenamesidd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            timesidd=int(linesidd.split(" ")[0])		

            self.kaons_on_lumi=float(linesidd.split(" ")[2])		

            if(now - timesidd > 350):
                if(self.lmerrcounter < 10 ):
                    self.lmerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: LM push not updating.")
                if(self.lmerrcounter == 10 ):
                    self.lmerrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: LM push not updating - suppressing.")
            else:
                if self.lmerrcounter > 5:
                    self.send_message(None, context, "ℹ️ *INFO* ℹ️: LM back online")

                self.lmerrcounter = 0
                self.lmok=True
        except Exception as e:
            # logging.error(f"Error executing tail command: {e.stderr.decode('utf-8')}")
            logging.error(f"An error occurred: {str(e)}")

            timesidd=0
            self.kaons_on_lumi = 0
            if(self.lmerrcounter < 10 ):
                self.lmerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: LM push not present.")
            if(self.lmerrcounter == 10 ):
                self.lmerrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: LM push not present - suppressing.")

    def check_sdd_push(self, context):
        chat_id=context.job.context
        now=int(time.time())
        try:
            linesidd = subprocess.run(['tail', '-1', self.filenamesidd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            timesidd=int(linesidd.split(" ")[0])		

            self.kaons_on_lumi=float(linesidd.split(" ")[2])		


            linesiddsdd = subprocess.run(['tail', '-1', self.filenamesiddsdd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            # linesiddsdd = subprocess.run(['tail', '-1', filenametest], stdout=subprocess.PIPE).stdout.decode('utf-8')
            timesiddsdd=int(linesiddsdd.split(" ")[0])
            if(now - timesiddsdd > 350): # not updating
                if self.sdderrcounter < 10:
                    self.sdderrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: SDD push not updating.")
                    oldsiddhartalastupdate=int(os.path.getmtime(self.filenameoldsiddharta))
                    if(now - oldsiddhartalastupdate > 350):
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: ORIGINAL SDD push not updating.")
                if self.sdderrcounter == 10:
                    self.sdderrcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: SDD push not updating - suppressing.")
                    oldsiddhartalastupdate=int(os.path.getmtime(self.filenameoldsiddharta))
                    if(now - oldsiddhartalastupdate > 350):
                        self.send_message(None, context, "⚠️ *WARNING* ⚠️: ORIGINAL SDD push not updating - suppressing.")


            else: #updating
                if self.sdderrcounter > 5:
                    self.send_message(None, context, "ℹ️ *INFO* ℹ️: SDD push back online")
                self.sdderrcounter = 0
                self.sddok=True

                    # ------- check if rates are blocked ------- #
                try:
                    # linetest = subprocess.run(['tail', '-1', filenametest], stdout=subprocess.PIPE).stdout.decode('utf-8')
                    # kaonsrate = float(linetest.split(" ")[2].strip())
                    # kaonsrate = float(linesiddsdd.split(" ")[2].strip())
                    fields = linesiddsdd.strip().split(" ")
                    # logger.info("linesiddsdd "+linesiddsdd)
                    # logger.info(len(fields))
                    if len(fields) >= 3:
                        kaonsrate = float(fields[2].strip())
                    else:
                        kaonsrate = 0
                        self.logger.info("missing field in siddharta2 push")

                    if (kaonsrate == self.kaonsrateold) and self.beamin and kaonsrate>0.5:
                        self.kaonsratecntr+=1
                    else:
                        self.kaonsratecntr=0
                    # logger.info(self.kaonsratecntr)

                    if self.kaonsratecntr > 10: 
                        if self.kaonserrcounter < 10:
                            self.kaonserrcounter+=1
                            self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAQ (probably) stuck, please check.")
                        if self.kaonserrcounter == 10:
                            self.kaonserrcounter+=1
                            self.send_message(None, context, "⚠️ *WARNING* ⚠️: DAQ (probably) stuck, please check - suppressing.")

                    else:
                        if self.kaonserrcounter > 5:
                            self.send_message(None, context, "ℹ️ *INFO* ℹ️: DAQ (probably) back")
                        self.kaonserrcounter = 0
                    self.kaonsrateold = kaonsrate
                except:
                    self.logger.info("something went wrong")		
                try:		
                    # logger.info(self.kaons_on_lumi)
                    # logger.info(kaonsrate)
                    ## ----------------- check if kaons on lumi but not on SIDD ------------ #
                    if self.kaons_on_lumi > 1 and kaonsrate < 1: 
                        self.kaonsratecntr2+=1
                    else:
                        self.kaonsratecntr2=0	
                    # logger.info(self.kaonserrcounter2)
                    # logger.info(self.kaonsratecntr2)		
                    # logger.info("good 1")		

                    if self.kaonsratecntr2 > 10:
                        if self.kaonserrcounter2 < 10:
                            self.kaonserrcounter2+=1
                            self.send_message(None, context, "⚠️ *WARNING* ⚠️: Kaons on Lumi but not on SIDDHARTA2, please check")
                        if self.kaonserrcounter2 == 10:
                            self.kaonserrcounter2+=1
                            self.send_message(None, context, "⚠️ *WARNING* ⚠️: Kaons on Lumi but not on SIDDHARTA2 - suppressing.")

                    else:
                        if self.kaonserrcounter2 > 5:
                            self.send_message(None, context, "ℹ️ *INFO* ℹ️: Kaons back on SIDDHARTA2")
                        self.kaonserrcounter2 = 0
                except:
                    self.logger.info("something went wrong again")

        except Exception as e:
            # logging.error(f"Error executing tail command: {e.stderr.decode('utf-8')}")
            logging.error(f"An error occurred: {str(e)}")

            timesiddsdd=0
            # print(self.sdderrcounter)
            if self.sdderrcounter < 10:
                self.sdderrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: SDD push not present.")
            if self.sdderrcounter == 10:
                self.sdderrcounter+=1
                self.send_message(None, context, "⚠️ *WARNING* ⚠️: SDD push not present - suppressing.")

    def check_global(self, context):
        chat_id=context.job.context

        if not self.maskGlobalStatus:
            if(self.dafneok and self.beamin and self.sddok	and not self.lmok):
                self.send_message(None, context, "❌ *ERROR* ❌: DAFNE running but LM is not.")
                time.sleep(0.2)
                self.send_message(None, context, "❌ *ERROR* ❌: DAFNE running but LM is not.")

            if( self.dafneok and self.beamin and not self.sddok	):

                self.send_message(None, context, "❌ *CRITICAL* ❌: DAFNE running but SDD not.")
                time.sleep(0.2)
                self.send_message(None, context, "❌ *CRITICAL* ❌: DAFNE running but SDD not.")
                time.sleep(0.2)
                self.send_message(None, context, "❌ *CRITICAL* ❌: DAFNE running but SDD not.")
                time.sleep(0.2)
                self.send_message(None, context, "❌ *CRITICAL* ❌: DAFNE running but SDD not.")
                time.sleep(0.2)
                self.send_message(None, context, "❌ *CRITICAL* ❌: DAFNE running but SDD not.")

    def check_czt_global(self,context):
        
        chat_id=context.job.context

        if not self.maskCZT:
            if( (self.dafneok and self.beamin and self.lmok) and (self.process is None)):
                if(self.cztcounter < 3 ):
                    self.cztcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: CZT Checker not running but beam in.")
                if(self.cztcounter == 3 ):
                    self.cztcounter+=1
                    self.send_message(None, context, "⚠️ *WARNING* ⚠️: CZT Checker not running but beam in - suppressing.")
            elif (self.process is not None):
                if self.cztcounter > 1:
                    self.send_message(None, context, "ℹ️ *INFO* ℹ️: CZT Checker back online.")
                    self.cztcounter = 0


    def check_pings(self, context):
        chat_id=context.job.context

        if not self.maskPings:
            checkpccr1=self.ping("___PC_IP___")
            if(not checkpccr1):

                self.send_message(None, context, "⚠️ *WARNING* ⚠️: pccr1 down")
            checkusersdd=self.ping("__your_ip___")
            if(not checkusersdd):

                self.send_message(None, context, "❌ *ERROR* ❌: usersdd down")
                self.send_message(None, context, "❌ *ERROR* ❌: usersdd down")



    def callback_minute(self, context):
        """Send a message when the command /start is issued."""
        chat_id=context.job.context


        self.update_file_paths()



        self.dafneok = False
        self.beamin  = False
        self.lmok    = False
        self.sddok   = False
        self.slctrok = False


        # ---------------------------- #
        # ------- DAFNE PUSH --------- #
        # ---------------------------- #

        self.check_dafne_push(context)
        # ---------------------------- #
        # ----- SLOW CRL PUSH -------- #
        # ---------------------------- #
        self.check_slowcontrol_push(context)

        # ---------------------------- #
        # -------- LUMI PUSH --------- #
        # ---------------------------- #
        self.check_lumi_push(context)
        
        # ---------------------------- #
        # --------- SDD PUSH --------- #
        # ---------------------------- #
        self.check_sdd_push(context)

      
        # ---------------------------- #
        # --------- GLOBAL ----------- #
        # ---------------------------- #

        self.check_global(context)

        # ---------------------------- #
        # ---------  CZT  ------------ #
        # ---------------------------- #

        self.check_czt_global(context)

        # ---------------------------- #
        # ---------- PING ------------ #
        # ---------------------------- #

        self.check_pings(context)

    # sets the alarms to the actual present values
    @restricted
    def setalarms(self, update, context):
        # load the present values
        try:    
            lineslowcontrol = subprocess.run(['tail', '-1', self.filenameslowcontrol], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            pressureTarget=float(lineslowcontrol.split("\t")[13])
            vaccumPressure=float(lineslowcontrol.split("\t")[14])
            tsdd1=float(lineslowcontrol.split("\t")[1])
            tsdd2=float(lineslowcontrol.split("\t")[2])
            tsdd3=float(lineslowcontrol.split("\t")[3])
            tsdd4=float(lineslowcontrol.split("\t")[4])
            tsdd5=float(lineslowcontrol.split("\t")[5])
            tsdd6=float(lineslowcontrol.split("\t")[6])
            tsdda=float(lineslowcontrol.split("\t")[7])
            tsddb=float(lineslowcontrol.split("\t")[8])
            tsddc=float(lineslowcontrol.split("\t")[9])
            tsddd=float(lineslowcontrol.split("\t")[10])
            tsdr1=float(lineslowcontrol.split("\t")[16])
            tsdr2=float(lineslowcontrol.split("\t")[18])


            code = {
                "alarms_dict": {
                    "pressure": [pressureTarget * 0.9 ,pressureTarget * 0.95  ,pressureTarget * 1.05 ,pressureTarget * 1.1  ],
                    "vacuum":   [0.0  ,0.0  ,5e-6  ,1e-5  ],
                    "tsdd1":   [-160  ,-160 ,-100  ,-100  ],
                    "tsdd2":   [-160 ,-160  ,-100  ,-100  ],
                    "tsdd3":   [-160 ,-160  ,-100  ,-100  ],
                    "tsdd4":   [-160 ,-160 ,-100  ,-100  ],
                    "tsdd5":   [-160 ,-160 ,-100  ,-100  ],
                    "tsdd6":   [-160 ,-160 ,-100  ,-100  ],
                    "tsdda":   [tsdda-2  ,tsdda-1  ,tsdda+1  ,tsdda+2],
                    "tsddb":   [tsddb-2  ,tsddb-1  ,tsddb+1  ,tsddb+2],# important
                    "tsddc":   [tsddc-2  ,tsddc-1  ,tsddc+1  ,tsddc+2],
                    "tsddd":   [0.0  ,0.0  ,200    ,200    ], #was 76 and 77 ; stopped working 18.03
                    "tsdr1":   [tsdr1-2  ,tsdr1-1  ,tsdr1+1    ,tsdr1+2  ], # important
                    "tsdr2":   [tsdr2-2  ,tsdr2-1  ,tsdr2+1    ,tsdr2+2  ], # important
                }
            }
            with open('alarms_siddharta2.json', 'w') as f:
                json.dump(code,f)
            self.as2 = self.get_updated_values()
            self.send_message(update, context, "ℹ️ *INFO* ℹ️: Alarms set to the present values")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            self.send_message(update, context, "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error")

    # send snapshots of grafana
    @restricted
    def snap(self, update, context):
        command1= 'curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta2-slow-control?orgId=1&refresh=1m&from=now-12h&to=now&panelId=11&width=1000&height=500&tz=Europe%2FRome" > /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command1) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))
        command3= 'curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta-sdd-rates-expert?orgId=1&refresh=1m&from=now-3h&to=now&panelId=32&width=1000&height=500&tz=Europe%2FRome" > /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command3) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))
        command4='curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta-sdd-rates-expert?orgId=1&refresh=1m&from=now-3h&to=now&panelId=2&width=1000&height=500&tz=Europe%2FRome"> /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command4) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))

    # send snapshots of grafana
    @restricted
    def snapsl(self, update, context):
        command1= 'curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta2-slow-control?orgId=1&refresh=1m&from=now-5h&to=now&panelId=4&width=1000&height=500&tz=Europe%2FRome" > /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command1) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))

        command2= 'curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta2-slow-control?orgId=1&refresh=1m&from=now-5h&to=now&panelId=8&width=1000&height=500&tz=Europe%2FRome" > /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command2) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))
        command3= 'curl -H "Authorization: Bearer ___your_auth_token___=" "http://___your_grafana_ip___:3000/render/d-solo/xxx/siddharta2-slow-control?orgId=1&refresh=1m&from=now-5h&to=now&panelId=9&width=1000&height=500&tz=Europe%2FRome" > /home/fnapolit/control/telegramnotifs/test.png '
        os.system(command3) # apologies
        context.bot.send_photo(chat_id=update.message.chat_id,photo=open('/home/fnapolit/control/telegramnotifs/test.png','rb'))

    @restricted
    def emergencyrestart(self, update, context):
        command="ssh -i ~/.ssh/4usersdd ___your_user___@__your_ip___ /bin/bash /home/usersdd/control/launchall.sh"
        context.bot.send_message(chat_id=update.message.chat_id,text='ℹ️ *INFO* ℹ️: Safe restart of services which were down on usersdd...', parse_mode= 'Markdown')
        os.system(command)

    @restricted
    def presentMaskOptions(self,update,context):
        context.bot.send_message(chat_id=update.message.chat_id,text='ℹ️ *INFO* ℹ️: Masks options are and status is ...', parse_mode= 'Markdown')
        if self.maskPressure:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskPressure  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskPressure  status False', parse_mode= 'Markdown')
        time.sleep(0.5)

        if self.maskVacuum:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskVacuum  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskVacuum  status False', parse_mode= 'Markdown')
        time.sleep(0.5)
        if self.maskTemperature:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskTemperature  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskTemperature  status False', parse_mode= 'Markdown')
        time.sleep(0.5)
        if self.maskGlobalStatus:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskGlobalStatus  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskGlobalStatus  status False', parse_mode= 'Markdown')
        time.sleep(0.5)
        if self.maskCZT:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskCZT  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskCZT  status False', parse_mode= 'Markdown')
        time.sleep(0.5)
        if self.maskPings:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskPings  status True ⚠️ Masked', parse_mode= 'Markdown')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,text='/maskPings  status False', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='ℹ️ *INFO* ℹ️: To unmask ...', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskPressure', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskVacuum', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskTemperature', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskGlobalStatus', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskCZT', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskPings', parse_mode= 'Markdown')
        time.sleep(0.5)
        context.bot.send_message(chat_id=update.message.chat_id,text='/unMaskAll', parse_mode= 'Markdown')


    @restricted
    def maskPressureOpt(self,update,context): 
        self.maskPressure       = True
        context.bot.send_message(chat_id=update.message.chat_id,text='Pressure alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def maskVacuumOpt(self,update,context): 
        self.maskVacuum         = True
        context.bot.send_message(chat_id=update.message.chat_id,text='Vacuum alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def maskTemperatureOpt(self,update,context): 
        self.maskTemperature    = True
        context.bot.send_message(chat_id=update.message.chat_id,text='Temperatures alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def maskGlobalStatusOpt(self,update,context): 
        self.maskGlobalStatus   = True
        context.bot.send_message(chat_id=update.message.chat_id,text='Global Status alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def maskCZTOpt(self,update,context): 
        self.maskCZT   = True
        context.bot.send_message(chat_id=update.message.chat_id,text='CZT Status alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def maskPingsOpt(self,update,context): 
        self.maskPings          = True
        context.bot.send_message(chat_id=update.message.chat_id,text='Ping alarm is ⚠️ Masked', parse_mode= 'Markdown')

    @restricted
    def unMaskPressureOpt(self,update,context): 
        self.maskPressure       = False
        context.bot.send_message(chat_id=update.message.chat_id,text='Pressure alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskVacuumOpt(self,update,context): 
        self.maskVacuum         = False
        context.bot.send_message(chat_id=update.message.chat_id,text='Vacuum alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskTemperatureOpt(self,update,context): 
        self.maskTemperature    = False
        context.bot.send_message(chat_id=update.message.chat_id,text='Temperatures alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskGlobalStatusOpt(self,update,context): 
        self.maskGlobalStatus   = False
        context.bot.send_message(chat_id=update.message.chat_id,text='Global status alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskCZTOpt(self,update,context): 
        self.maskCZT   = False
        context.bot.send_message(chat_id=update.message.chat_id,text='CZT status alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskPingsOpt(self,update,context): 
        self.maskPings          = False
        context.bot.send_message(chat_id=update.message.chat_id,text='Ping alarm is ℹ️ unmasked', parse_mode= 'Markdown')

    @restricted
    def unMaskAllOpt(self,update,context): 
        self.maskPressure       = False
        self.maskVacuum         = False
        self.maskTemperature    = False
        self.maskGlobalStatus   = False
        self.maskCZT            = False
        self.maskPings          = False
        context.bot.send_message(chat_id=update.message.chat_id,text='All alarms are ℹ️ unmasked', parse_mode= 'Markdown')


    def main(self,updater):
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start",self.start, pass_job_queue=True))
        dp.add_handler(CommandHandler("restart",self.restart, pass_job_queue=True))
        dp.add_handler(CommandHandler("stop",self.stop, pass_job_queue=True))
        dp.add_handler(CommandHandler("snap",self.snap, pass_job_queue=True))
        dp.add_handler(CommandHandler("snapsl",self.snapsl, pass_job_queue=True))
        dp.add_handler(CommandHandler("emergencyrestart",self.emergencyrestart, pass_job_queue=True))
        dp.add_handler(CommandHandler("masks",self.presentMaskOptions, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskPressure",self.maskPressureOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskVacuum",self.maskVacuumOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskTemperature",self.maskTemperatureOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskGlobalStatus",self.maskGlobalStatusOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskCZT",self.maskCZTOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("maskPings",self.maskPingsOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskPressure",self.unMaskPressureOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskVacuum",self.unMaskVacuumOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskTemperature",self.unMaskTemperatureOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskGlobalStatus",self.unMaskGlobalStatusOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskCZT",self.unMaskCZTOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskPings",self.unMaskPingsOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler("unMaskAll",self.unMaskAllOpt, pass_job_queue=True))
        dp.add_handler(CommandHandler('start_cztchecker',self.start_cztchecker))
        dp.add_handler(CommandHandler('stop_cztchecker',self.stop_cztchecker))
        dp.add_handler(CommandHandler('setalarms',self.setalarms))
        dp.add_handler(CommandHandler('help',self.help_command))  # Add this line

        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    my_bot = siddharta2_bot()
    my_bot.main(my_bot.updater)

