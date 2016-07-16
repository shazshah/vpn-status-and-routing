#Author:    Shaz
#
#Date:      16/07/2016
#
#Purpose:   If a client machine is connect to vpn a client and you attempt to connect to that
#           client machine via your own VPN Server (i.e. through VPN server on a router)
#           the client machine will be inaccesible. This script will apply routing tables on the
#           client machine it is run on so that the client machine is aware of the router and 
#           therefore visible to the VPN Server.
#
#Usage:     Save the script in a location (any), modify the accompanying com.xxxx.plist
#           so that it points to this script file. Copy the plist into /Library/LaunchDaemons using sudo.
#           Load the plist using sudo launchctl load -w /Library/LaunchDaemons/xxxxx.plist. By default the
#           property file is configured to run every 30 minutes.

import os, datetime, subprocess

#-----Global Variables-----

#specify where the log file and the flag should be saved
log_file_path = "/Users/shazshah/Documents/scripts/route-log.txt"
successful_ip_tables_log_flag = ("/Users/shazshah/Documents/scripts/ip-tables-run-successfully.txt")

#-----CLASSES-----
class Get_Time_Date(object):
    def time_date_now(self):
        now = datetime.datetime.now()
        date_time_now = now.strftime("%Y-%m-%d %H:%M")
        return date_time_now

class Text_File_Modifier(object):
    #check if a log file already exists and is 10 or more lines long, if true, delete.
    def delete_file(self, file_path):
        if os.path.isfile(log_file_path) == True:
            count_lines = 0
            with open (log_file_path, 'rb') as f:
                for line in f:
                    count_lines += 1
            if count_lines == 10:
                os.remove(log_file_path)

    def write_file(self, input_string, file_path):
        #check if a log file already exists and is 10 or more lines long, if true, delete.
        delete_log = Text_File_Modifier()
        delete_log.delete_file(file_path)

        #create a log file with each line beginning with date/time
        log_time = Get_Time_Date().time_date_now()
        text_file = open(file_path, "a")
        text_file.write("%s : %s \n" % (log_time, input_string))
        text_file.close()

class Get_VPN_Status(object):
    def read_vpn_status(self):
        #run shell command to get vpn status
        f = os.popen('ifconfig | grep -c utun0')
        status = f.read()
        return status

    def test_vpn_status(self):
    	#if the status returns 1 then vpn is connected    	
        is_vpn_connected = Get_VPN_Status()
    	if int(is_vpn_connected.read_vpn_status()) == 1:
    		return True
    	else:
            log_file = Text_File_Modifier()
            log_file.write_file("I am NOT connected to VPN.", log_file_path)
            if os.path.isfile(successful_ip_tables_log_flag) == True:
                log_file.write_file("VPN is disconnected. Deleting flag file ip-tables-run-successfully.txt so IP tables can be applied on next VPN connection", log_file_path)
                os.remove(successful_ip_tables_log_flag)
            return "I am NOT connected to VPN."

class Write_IP_Tables(object):
    def run_ip_tables_command(self):
        vpn_on = Get_VPN_Status().test_vpn_status
        log_file = Text_File_Modifier()
        if vpn_on() == True:
            if os.path.isfile(successful_ip_tables_log_flag) == False: #ip tables have not been run successfully before i.e. no flag log exists
                #run shell command to add route
                route_ip = subprocess.Popen(["route", "add", "-host", "10.8.0.0", "-netmask", "255.255.255.0", "192.168.1.1"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                output = route_ip.communicate()[0]
                
                log_file.write_file("VPN Connected. Running IP Tables.", log_file_path)
                log_file.write_file("IP Tables run successfully. Successful Log Flag created.", successful_ip_tables_log_flag)
                return "IP Tables run successfully. Successful Log Flag created."
            else:
                log_file.write_file("Already run successfully, not running again!", log_file_path)
                return "Already run successfully, not running again!"

        else:
            log_file = Text_File_Modifier()
            log_file.write_file("Unable to run IP tables.", log_file_path)
            return "Unable to run IP tables."

#-----MAIN-----

#initialise class objects
#get_vpn_status = Get_VPN_Status()
write_ip_tables = Write_IP_Tables()

#begin attempting to write ip tables
write_ip_tables.run_ip_tables_command()