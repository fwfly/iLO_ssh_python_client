import paramiko
import uefi_menu_paser

import sys
import time
import datetime
import re


CMD_DEV_OK = "\x1b[0n"
CMD_DOWN = "\x1b[B"
CMD_UP = "\x1b[A"
CMD_ESC_9 = "\x1b9"
CMD_ENTER = "\x1bM"

class RemoteRbsuClient:
	def __init__(self, hostname, username, password):
		self.hostname = hostname
		self.username = username
		self.password = password
		self.port = 22
		self.session = None
		self.client = None
		self.esc_filter = True
		self.timestemp = datetime.datetime.now()
		self.uefi_helper = uefi_menu_paser.UefiMenuParser()

	def __check_ilo_selection(self, data):
		if (">" in data) and not ("l>" in data) and not ("\\>" in data):
			pattern = "\\x1b\[[0-9]+(:|;)+[0-9]+H|\\x1b\[[0-9]+m"
			pattern_data = re.sub(pattern, "", data)
			if ("> " == pattern_data[-2:]) or (">" == pattern_data[-1:]):
				return False
		return True

	def __update_timestemp(self):
		self.timestemp = datetime.datetime.now()

	def __check_time_out(self):
		cur_time = datetime.datetime.now()
		dt = cur_time - self.timestemp
		dt = dt.seconds
		if dt > 300:
			self.close_connect()
			print "Error : exit with timeout"
			sys.exit(1)

	def recv_data(self):
		session = self.session
 
		#self.__check_time_out()

		data=""
		if session.recv_ready():

			self.__update_timestemp()

			finished_collect = False
			while not finished_collect:
				newdata=""
				newdata = session.recv(1024)
				if 0 == len(newdata.strip()):
					finished_collect = True
				elif "-/" == newdata[-2:]:
					finished_collect = True
				elif "\r\n" == newdata[-2:]:
					finished_collect = True
				elif "[40m" == newdata[-4:]:
					finished_collect = self.__check_ilo_selection(data + newdata)
				elif "\x1b[1m\x1b[37m\x1b[40m" in data:
					finished_collect = self.__check_ilo_selection(data + newdata)
				elif "\x1b[5n" in data:
					finished_collect = True
				data = data + newdata
				print "---%r" %newdata 
			self.uefi_helper.parse(data)

		if self.esc_filter:
			pattern = "\\x1b\[[0-9]+(:|;)+[0-9]+H|\\x1b\[[0-9]+m"
			data = re.sub(pattern, "", data)
			if 0 == len(data.strip()):
				return ""
		print "====%r" %data
		return data

	def exec_cmd(self, cmd):
		self.session.exec_command(cmd)

	def connect(self):
		PORT = 22
		self.client = paramiko.Transport((self.hostname, self.port))
		self.client.connect(username=self.username, password=self.password)
		self.session = self.client.open_channel(kind="session")
		self.session.exec_command("vsp")
		#self.session.settimeout(50.0)


	def change_to_shell(self):
		self.session.close()
		self.session = self.client.open_channel(kind="session")
                #self.session.settimeout(50.0)
		self.session.invoke_shell()
		self.stdin = self.session.makefile('wb')
	

	def shell_execute(self, cmd):
		self.stdin.write(cmd)

	def close_connect(self):
		self.session.close()
		self.client.close()

	def set_esc_code_filter(self, enable):
		'''
			Enable/Disable esc code filter.
			Default is enable
		'''
		self.esc_filter = enable

def rrbsu_catch_rbsu_gui(HOST, username, password):
	r_client = RemoteRbsuClient(HOST, username, password)
        r_client.connect()
	#r_client.set_esc_code_filter(False)
	while True:
		data = r_client.recv_data()
                if "\x1b[5n" in data:
			r_client.exec_cmd(CMD_DEV_OK)
	        elif "few moments" in data:
			print "----Send ESC + 9"
			r_client.exec_cmd(CMD_ESC_9)

			# UEFI menu is interacted with shell mode.
			r_client.change_to_shell()
			break


	while True:
		data = r_client.recv_data()
		if ">" in data:
			if "> System Configuration" in data:
				print "----Selecting System Configuration"
				r_client.shell_execute("\r")
				break
			else:
				r_client.shell_execute(CMD_DOWN)

	while True:
		data = r_client.recv_data()
		if ">" in data:
			if "> BIOS/Platform" in data:
				r_client.shell_execute("\r")
				break
			else:
				r_client.shell_execute(CMD_DOWN)

	while True:
                data = r_client.recv_data()
		if ">" in data:
			if "> PCI Device Enable" in data:
				r_client.shell_execute("\r")
				break
			else:
				r_client.shell_execute(CMD_DOWN)

		
	r_client.close_connect()


#if __name__ == '__main__' :
#	if len(sys.argv) < 4:	
#		usage = "Usage : python %s <hostname> <username> <password>" % __file__[__file__.rfind('/')+1:]
#        	print usage
#        	sys.exit(1)

rrbsu_catch_rbsu_gui("15.119.204.206", "Administrator", "password@123")
