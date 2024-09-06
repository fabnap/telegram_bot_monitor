from cgitb import reset
import unittest
import time
from unittest.mock import MagicMock, patch
from main import siddharta2_bot
# import alarms_siddharta2 as as2
import requests
import json 

# these are used to create the suitable scenario for the tests
# Define the file paths for each file
file_paths = {
    "slow_control": "/home/fnapolit/control/testslowcontrol.txt",
    "sidd": "/home/fnapolit/control/testssidd.txt",
    "dafne": "/home/fnapolit/control/testsdafne.txt",
    "lumi": "/home/fnapolit/control/testslumi.txt",
    "oldsidd": "/home/fnapolit/control/test_oldsiddharta.txt",
}

# Initial data for each file
data = {
    "slow_control": [
        "23-Mar-23 7:21:45 PM",
    -140.179630,-145.540897,-142.548324,-137.178730,-138.413383,-145.335072,26.528100,25.998000,27.079900,31.063200,-140.618696,-141.025724,1.336625,0.000000291,20.601700,126.001000,34.178500,125.999000,1.391833, 1.386163,1418.306250,25.534690,42.799239,45.900000,44.700000,34.000000
    ],
    "sidd": [
        int(time.time()),
        100,
        30,
    ],
    "dafne": [
        int(time.time()),
        1500,  # electrons
        1000,  # positrons
    9,100,100,0,0,-1459,27,-1,-1,0,2.42637,-1,0,0,-1,-1,-1,-1,-1,-1,-1,-1,0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,27.5265,27.7584,48.3333,0,1.00254,0,0,0 # rest is not important

    ],
    "lumi": [
        int(time.time()),
        300,
        100,
        30,
        15.00,
    ],
    "oldsidd": [
        1,
        1,
        1,
    ]
}


current_time = int(time.time())
data["sidd"][0] = current_time
data["dafne"][0] = current_time
data["lumi"][0] = current_time

with open(file_paths["lumi"], "w") as file: 
    file.write(" ".join(map(str, data["lumi"])) + "\n")

class TestMyClass(unittest.TestCase):
    def setUp(self):
        self.siddharta2_bot = siddharta2_bot()
        self.context = MagicMock()
        self.update = MagicMock()
        self.context.job.context = "test_chat_id"
        self.siddharta2_bot.TEST_MODE = True
        self.siddharta2_bot.update_file_paths()
        self.siddharta2_bot.allowed_start_stop = [1338624902, -509331538]
        self.as2 = self.get_updated_values()


    def get_updated_values(self):
        with open('alarms_siddharta2.json', 'r') as f:
            data = json.load(f)
        return data

        # ---------------------------- #
        # -------- LUMI PUSH --------- #
        # ---------------------------- #

    def test_check_lumi_push_lm_back_online(self):

        data["lumi"][0] = current_time
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        # Simulate the case where LM is back online
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 6
        self.siddharta2_bot.check_lumi_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️: LM back online")

    def test_check_lumi_push_lm_push_not_updating(self):

        data["lumi"][0] = current_time - 1000
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        # Simulate the case where LM push is not updating
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 8
        self.siddharta2_bot.check_lumi_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not updating.")

    def test_check_lumi_push_lm_push_invalid(self):

        data["lumi"][0] = current_time - 1000
        data["lumi"][2] = 's'
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        # Simulate the case where LM push is not updating
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 8
        self.siddharta2_bot.check_lumi_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not present.")
        # reset mock object
        self.siddharta2_bot.send_message.reset_mock()
        data["lumi"][2] = ''
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        # Simulate the case where LM push is not updating
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 8
        self.siddharta2_bot.check_lumi_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not present.")
        data["lumi"][2] = 100




    def test_check_lumi_push_lm_push_not_updating_suppressing(self):
        # Simulate the case where LM push is not updating

        data["lumi"][0] = current_time - 1000
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 10
        self.siddharta2_bot.check_lumi_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not updating - suppressing.")


    def test_check_lumi_push_lm_push_not_present(self):
        # Simulate the case where LM push is not present
        self.siddharta2_bot.filenamesidd = "/not/present/file"

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 2
        self.siddharta2_bot.check_lumi_push(self.context)

        # self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not present.")
        
    def test_check_lumi_push_lm_push_not_present_suppressing(self):
        # Simulate the case where LM push is not present
        self.siddharta2_bot.filenamesidd = "/not/present/file"

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.lmerrcounter = 10
        self.siddharta2_bot.check_lumi_push(self.context)

        # self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: LM push not present - suppressing.")


    # ---------------------------- #
    # -------  SDD  PUSH --------- #
    # ---------------------------- #


    @patch('subprocess.run')
    @patch('os.path.getmtime')
    def test_check_sdd_push_sdd_not_updating(self, mock_getmtime,mock_subprocess):
        # Simulate the case where SDD push is not updating
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 400} 0 0"
        mock_getmtime.return_value = int(time.time()) - 400

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.sdderrcounter = 0
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 2)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "⚠️ *WARNING* ⚠️: SDD push not updating.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[1][0][2], "⚠️ *WARNING* ⚠️: ORIGINAL SDD push not updating.")
        # reset mock object
        self.siddharta2_bot.send_message.reset_mock()
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 400} 0 0"
        mock_getmtime.return_value = int(time.time()) - 0

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.sdderrcounter = 0
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "⚠️ *WARNING* ⚠️: SDD push not updating.")


    @patch('subprocess.run')
    @patch('os.path.getmtime')
    def test_check_original_sdd_push_sdd_not_updating(self, mock_getmtime, mock_subprocess):
        # Simulate the case where SDD push is not updating
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 400} 0 0"
        mock_getmtime.return_value = int(time.time()) - 400
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.sdderrcounter = 0
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 2)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "⚠️ *WARNING* ⚠️: SDD push not updating.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[1][0][2], "⚠️ *WARNING* ⚠️: ORIGINAL SDD push not updating.")

    @patch('subprocess.run')
    def test_check_sdd_push_sdd_back_online(self, mock_subprocess):
        # Simulate the case where SDD push is back online
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 0} 0 0"
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.sdderrcounter = 6
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️: SDD push back online")

    @patch('subprocess.run')
    def test_check_sdd_push_daq_stuck(self, mock_subprocess):
        # Simulate the case where DAQ is stuck
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 0} 0 1"
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.kaonsrateold = 0
        self.siddharta2_bot.kaonsratecntr = 0
        self.siddharta2_bot.beamin = True
        for i in range(0, 13):
            self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 2)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: DAQ (probably) stuck, please check.")

    @patch('subprocess.run')
    def test_check_sdd_push_daq_back(self, mock_subprocess):
        # Simulate the case where DAQ is back
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 0} 0 2"
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.kaonsrateold = 1
        self.siddharta2_bot.kaonsratecntr = 0
        self.siddharta2_bot.kaonserrcounter = 6
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️: DAQ (probably) back")

    @patch('subprocess.run')
    def test_check_sdd_push_invalid_character(self, mock_subprocess):
        # Simulate the case where DAQ is back
        mock_subprocess.return_value.stdout.decode.return_value = f"{int(time.time()) - 0} 0 k"
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.kaonsrateold = 0
        self.siddharta2_bot.kaonsratecntr = 0
        self.siddharta2_bot.kaonserrcounter = 0
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: SDD push not present.")


    def test_check_kaons_on_lumi_not_on_siddharta2(self):
        # Simulate the case where there are kaons on lumi but not on SIDDHARTA2

        data["lumi"][0] = current_time
        with open(file_paths["lumi"], "w") as file: 
            file.write(" ".join(map(str, data["lumi"])) + "\n")

        data["sidd"][0] = current_time
        data["sidd"][1] = 0
        data["sidd"][2] = 0

        with open(file_paths["sidd"], "w") as file: 
            file.write(" ".join(map(str, data["sidd"])) + "\n")
        self.siddharta2_bot.send_message = MagicMock()
        for i in range(0, 11):

            self.siddharta2_bot.check_sdd_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: Kaons on Lumi but not on SIDDHARTA2, please check")


    @patch('os.path.getmtime')
    def test_check_slowcontrol_push(self,mock_getmtime):

        # Simulate the case where the last update was more than 350 seconds ago
        mock_getmtime.return_value = int(time.time()) - 400

        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][3] = -140.
        data["slow_control"][4] = -140.
        data["slow_control"][5] = -140. 
        data["slow_control"][6] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2
        data["slow_control"][9] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][10] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][11] = -140.
        data["slow_control"][12] = -140.
        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2
        data["slow_control"][14] = 1e-8
        data["slow_control"][16] = (self.as2["alarms_dict"]['tsdr1'][1]+self.as2["alarms_dict"]['tsdr1'][2])/2
        data["slow_control"][18] = (self.as2["alarms_dict"]['tsdr2'][1]+self.as2["alarms_dict"]['tsdr2'][2])/2

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: Slow Control not updating")

    @patch('os.path.getmtime')
    def test_check_slowcontrol_push_not_present(self,mock_getmtime):

        # Simulate the case where the last update was more than 350 seconds ago
        mock_getmtime.return_value = int(time.time()) - 400


        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        self.siddharta2_bot.filenameslowcontrol = "/not/present/file"
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error")


    @patch('os.path.getmtime')
    def test_check_slowcontrol_push_pressure_high(self,mock_getmtime):

        # Simulate the case where the last update was more than 350 seconds ago
        mock_getmtime.return_value = int(time.time()) - 0


        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][3] = -140.
        data["slow_control"][4] = -140.
        data["slow_control"][5] = -140. 
        data["slow_control"][6] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2
        data["slow_control"][9] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][10] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][11] = -140.
        data["slow_control"][12] = -140.
        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1.06
        data["slow_control"][14] = 1e-8
        data["slow_control"][16] = (self.as2["alarms_dict"]['tsdr1'][1]+self.as2["alarms_dict"]['tsdr1'][2])/2
        data["slow_control"][18] = (self.as2["alarms_dict"]['tsdr2'][1]+self.as2["alarms_dict"]['tsdr2'][2])/2

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")


        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: PRESSURE TARGET HIGH")


        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1.3

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: PRESSURE TARGET HIGH - not suppressing - ACTION IS REQUIRED IMMEDIATELY")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*0.7

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: PRESSURE TARGET LOW - not suppressing - ACTION IS REQUIRED IMMEDIATELY")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-5

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: VACUUM PRESSURE > 1e-5 mbar - not suppressing - ACTION IS REQUIRED IMMEDIATELY")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = 200.

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = 200.

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 +100

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")
        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2 +100

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")



        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -200
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2 

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = -200

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 -100

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")
        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1
        data["slow_control"][14] = 2e-8
        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2 -100

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")
        for i in range(0, 11):
            self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "❌ *CRITICAL* ❌: TEMPERATURES DECREASING - TAKE ACTION IMMEDIATELY - not suppressing - SIDDHARTA2 IS IN DANGER.")


    @patch('os.path.getmtime')
    def test_check_invalid_characters(self,mock_getmtime):

        # Simulate the case where the last update was more than 350 seconds ago
        mock_getmtime.return_value = int(time.time()) - 0


        data["slow_control"][1] = -140.
        data["slow_control"][2] = -140.
        data["slow_control"][3] = -140.
        data["slow_control"][4] = '-'
        data["slow_control"][5] = -140. 
        data["slow_control"][6] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2
        data["slow_control"][9] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][10] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][11] = -140.
        data["slow_control"][12] = -140.
        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1.0
        data["slow_control"][14] = 1e-8
        data["slow_control"][16] = (self.as2["alarms_dict"]['tsdr1'][1]+self.as2["alarms_dict"]['tsdr1'][2])/2
        data["slow_control"][18] = (self.as2["alarms_dict"]['tsdr2'][1]+self.as2["alarms_dict"]['tsdr2'][2])/2

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")


        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error")
        # reset mock object
        self.siddharta2_bot.send_message.reset_mock()
        data["slow_control"][4] = ''

        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")


        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: Slow Control not present or parsing error")
        data["slow_control"][4] = -140.


    @patch('os.path.getmtime')
    def test_check_slowcontrol_multiple(self,mock_getmtime):

        # Simulate the case where the last update was more than 350 seconds ago
        mock_getmtime.return_value = int(time.time()) - 0


        data["slow_control"][1] = 0.
        data["slow_control"][2] = -140.
        data["slow_control"][3] = -140.
        data["slow_control"][4] = -140.
        data["slow_control"][5] = -140. 
        data["slow_control"][6] = -140.
        data["slow_control"][7] = (self.as2["alarms_dict"]['tsdda'][1]+self.as2["alarms_dict"]['tsdda'][2])/2 
        data["slow_control"][8] = (self.as2["alarms_dict"]['tsddb'][1]+self.as2["alarms_dict"]['tsddb'][2])/2
        data["slow_control"][9] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][10] = (self.as2["alarms_dict"]['tsddc'][1]+self.as2["alarms_dict"]['tsddc'][2])/2
        data["slow_control"][11] = -140.
        data["slow_control"][12] = -140.
        data["slow_control"][13] = (self.as2["alarms_dict"]['pressure'][1]+self.as2["alarms_dict"]['pressure'][2])/2*1.3
        data["slow_control"][14] = 1e-2
        data["slow_control"][16] = (self.as2["alarms_dict"]['tsdr1'][1]+self.as2["alarms_dict"]['tsdr1'][2])/2
        data["slow_control"][18] = (self.as2["alarms_dict"]['tsdr2'][1]+self.as2["alarms_dict"]['tsdr2'][2])/2


        with open(file_paths["slow_control"], "w") as file: 
            file.write("\t".join(map(str, data["slow_control"])) + "\n")



        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_slowcontrol_push(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 6)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "⚠️ *WARNING* ⚠️: PRESSURE TARGET HIGH")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[1][0][2], "❌ *CRITICAL* ❌: PRESSURE TARGET HIGH - gas will be released.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[2][0][2], "⚠️ *WARNING* ⚠️: VACUUM PRESSURE > 5e-6 mbar")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[3][0][2], "❌ *CRITICAL* ❌: VACUUM PRESSURE > 1e-5 mbar - LOOSING THE VACUUM - SDDs IN DANGER IF ON.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[4][0][2], "⚠️ *WARNING* ⚠️: TEMPERATURES out of range.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[5][0][2], "❌ *CRITICAL* ❌: TEMPERATURES INCREASING - TAKE ACTION IMMEDIATELY.")

    def test_check_global(self):
        # Simulate the case where DAFNE is running, the beam is in, but LM is not
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.sddok = True
        self.siddharta2_bot.lmok = False
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_global(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 2)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "❌ *ERROR* ❌: DAFNE running but LM is not.")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[1][0][2], "❌ *ERROR* ❌: DAFNE running but LM is not.")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        # Simulate the case where DAFNE is running, the beam is in, but SDD is not
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.sddok = False
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.check_global(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 5)
        for i in range(5):
            self.assertEqual(self.siddharta2_bot.send_message.call_args_list[i][0][2], "❌ *CRITICAL* ❌: DAFNE running but SDD not.")

    @patch.object(siddharta2_bot, 'ping')
    def test_check_pings(self, mock_ping):
        # Simulate the case where pccr1 is down and usersdd is up
        mock_ping.side_effect = [False, True]
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.check_pings(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "⚠️ *WARNING* ⚠️: pccr1 down")

        # Reset the mock object
        self.siddharta2_bot.send_message.reset_mock()

        # Simulate the case where pccr1 is up and usersdd is down
        mock_ping.side_effect = [True, False]
        self.siddharta2_bot.check_pings(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 2)
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[0][0][2], "❌ *ERROR* ❌: usersdd down")
        self.assertEqual(self.siddharta2_bot.send_message.call_args_list[1][0][2], "❌ *ERROR* ❌: usersdd down")


    def test_start(self):

        self.update.effective_chat.id = self.siddharta2_bot.allowed_start_stop[0]

        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.start_cztchecker = MagicMock()
        self.context.job_queue.run_repeating = MagicMock()
        
        siddharta2_bot.start.__wrapped__(self.siddharta2_bot, self.update, self.context)

        self.assertEqual(self.siddharta2_bot.dafenerrcounter, 0)
        self.assertEqual(self.siddharta2_bot.lmerrcounter, 0)
        self.assertEqual(self.siddharta2_bot.sdderrcounter, 0)
        # Add more assertions for the other counters here...
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️:Welcome to the SIDDHARTA2 telegram updater")
        self.assertEqual(self.siddharta2_bot.start_cztchecker.call_count, 1)
        self.assertEqual(self.context.job_queue.run_repeating.call_count, 1)

    def test_token_is_valid(self):
        response = requests.get(f'https://api.telegram.org/bot{self.siddharta2_bot.token}/getMe')
        # If the request was successful, the token is valid
        self.assertEqual(response.status_code, 200)


    def test_check_czt_global_czt_not_running_beam_in(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = None
        self.siddharta2_bot.cztcounter = 1

        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: CZT Checker not running but beam in.")

    def test_check_czt_global_czt_not_running_beam_in_masked(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = None
        self.siddharta2_bot.cztcounter = 1
        self.siddharta2_bot.maskCZT = True
        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 0)

    def test_check_czt_global_czt_not_running_beam_in_suppressing(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = None
        self.siddharta2_bot.cztcounter = 3

        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "⚠️ *WARNING* ⚠️: CZT Checker not running but beam in - suppressing.")

    def test_check_czt_global_czt_off_beam_lost(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = False
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = None
        self.siddharta2_bot.cztcounter = 4

        self.siddharta2_bot.check_czt_global(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 0)

    def test_check_czt_global_czt_on_beam_lost(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = False
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = MagicMock()
        self.siddharta2_bot.cztcounter = 4

        self.siddharta2_bot.check_czt_global(self.context)
        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️: CZT Checker back online.")

    def test_check_czt_global_czt_back_online(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = MagicMock()
        self.siddharta2_bot.cztcounter = 6

        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 1)
        self.assertEqual(self.siddharta2_bot.send_message.call_args[0][2], "ℹ️ *INFO* ℹ️: CZT Checker back online.")

    def test_check_czt_global_czt_running(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = True
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = MagicMock()
        self.siddharta2_bot.cztcounter = 1

        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 0)

    def test_check_czt_global_czt_running_no_beam(self):
        self.siddharta2_bot.send_message = MagicMock()
        self.siddharta2_bot.dafneok = True
        self.siddharta2_bot.beamin = False
        self.siddharta2_bot.lmok = True
        self.siddharta2_bot.process = MagicMock()
        self.siddharta2_bot.cztcounter = 0

        self.siddharta2_bot.check_czt_global(self.context)

        self.assertEqual(self.siddharta2_bot.send_message.call_count, 0)


if __name__ == '__main__':
    unittest.main()