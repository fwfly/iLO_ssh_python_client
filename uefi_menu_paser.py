###
# Copyright 2016 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# File Name: uefi_menu_paser.py
# Project : Morpheus-python-client 
###

'''
This class is for handling uefi menu and store current position in uefi.
It receive raw uefi data and analysizing it, then store position.
Other module can query this class to know what is current menu. 
'''

POSITION_DIALOG = "dialog"
POSITION_ROOT = "root"
POSITION_SYS_CONF = "System Cofigure"
POSITION_BIOS_CONF = "BIOS Configure"
POSITION_PCI_DEV_ENABLE_DISABLE = "PCI Device enable disable"

PATTERN_DIALOG = "--/"
PATTERN_MITEM_SYS_CONF = "System Conf"
PATTERN_MITEM_ONE_TIME_BOOT = "One-Time"
PATTERN_MITEM_BIOS_CONF = "\x1b[05;03HBIOS/Platform"
PATTERN_MHEAD_BIOS_CONF = "\x1b[01;01HBIOS/Platform"
PATTERN_MHEAD_DEV_ENABLE_DISABLE = "\x1b[03;01HPCI Device"

class UefiMenuParser:
	def __init__(self):
		self.current_position = [""]

	def parse(self, data):
		if (not self.isIn(POSITION_DIALOG)) and PATTERN_DIALOG in data:
			self.current_position.append(POSITION_DIALOG)
		elif PATTERN_MITEM_SYS_CONF in data:
			self.current_position[0] = POSITION_ROOT
		elif PATTERN_MITEM_BIOS_CONF in data:
			self.current_position[0] = POSITION_SYS_CONF
		elif PATTERN_MHEAD_DEV_ENABLE_DISABLE in data:
			self.current_position[0] = POSITION_PCI_DEV_ENABLE_DISABLE
		elif PATTERN_MHEAD_BIOS_CONF in data:
			self.current_position[0] = POSITION_BIOS_CONF
		else:
			pass # It didn't change current position if pattern doesn't match.

		if self.isIn(POSITION_DIALOG):
			if ">" in data:
				self.current_position.pop()
				
		#print "I'm in %s" %self.current_position[-1]

	def whereIsNow(self):
		return self.current_position[-1]

	def isIn(self, uefi_menu_string):
		if uefi_menu_string == self.current_position[-1]:
			return True
		return False
