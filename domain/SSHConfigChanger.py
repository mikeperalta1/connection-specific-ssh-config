

from domain.config.Config import Config
from domain.Logger import Logger


import os
import re
import subprocess
import sys


class SSHConfigChanger:
	
	__DEFAULT_NORMAL_SSH_CONFIG_FILE_NAME = "config"
	__DEFAULT_TARGET_NAME = "default"
	
	#
	def __init__(
			self,
			action_interface, action_command,
			config_file_path,
			dry_run: bool = False,
	):
		self.__logger = Logger(
		
		)
		
		self.__config = Config(
			logger=self.__logger,
			file_path=config_file_path
		)
		if dry_run:
			self.__logger.complain(f"Dry run enabled at runtime")
			self.__config.dry_run = True
		
		# Grab args
		self.__action_interface = action_interface
		self.__action_command = action_command
	
	def die(self, s):
		
		#
		self.__logger.complain(s)
		raise Exception(s)
	
	def quit(self, s):
		
		#
		self.__logger.log("Quitting because: " + s)
		sys.exit(0)
		
	#
	def run(self):
		
		self.__logger.log(
			f"Running for interface {self.__action_interface}: {self.__action_command}"
		)
		
		# Only run if an interface is coming up
		if self.__action_command != "up":
			self.quit(f"We don't need to run for action command: {self.__action_command}")
		
		# Determine which ssh config file we should use
		ssh_config_name = self.determine_ssh_config_name()
		if not ssh_config_name:
			self.die("Unable to determine appropriate ssh config name; Quitting")
		self.__logger.log(
			f"Determined ssh config name: {ssh_config_name}"
		)
		
		# Make paths
		ssh_config_path_link = self.__config.ssh_dir / self.__DEFAULT_NORMAL_SSH_CONFIG_FILE_NAME
		ssh_config_path_target = self.__config.ssh_dir / ssh_config_name
		self.__logger.log(
			f"Selecting source config file \"{ssh_config_path_target}\""
			f" for link \"{ssh_config_path_link}\""
		)
		
		# Don't run unless current ssh config is a symlink or not a file (for safety)
		self.require_symlink_or_none(ssh_config_path_link)
		
		if self.__config.dry_run:
			
			self.__logger.complain(
				f"Dry run enabled; Won't unlink existing symlink: {ssh_config_path_link}"
			)
			self.__logger.complain(
				f"Dry run enabled; Won't create symlink: {ssh_config_path_link} ==> {ssh_config_path_target}"
			)
			
		else:
		
			# Set the symlink
			if ssh_config_path_link.exists():
				try:
					ssh_config_path_link.unlink()
				except FileNotFoundError:
					pass
			
			ssh_config_path_link.symlink_to(ssh_config_path_target, target_is_directory=False)
		
		#
		self.__logger.log("Finished")
	
	#
	def require_symlink_or_none(self, file_path):
		
		#
		if ( not os.path.isfile(file_path) or os.path.islink(file_path) ):
			return True
		
		#
		self.die("For safety, we cannot continue if the target link exists and is a file (" + file_path + ")")
	
	def determine_ssh_config_name(self):
		
		#
		self.__logger.log("Attempting to determine SSH config name")
		
		# Check each section
		found_ssh_config_name = None
		for target_name in self.__config.targets:
			
			target = self.__config.targets[target_name]
			self.__logger.log(f"Examining target: {target_name}")
			
			# Don't examine default if anything is picked already
			if target_name == self.__DEFAULT_TARGET_NAME and found_ssh_config_name:
				self.__logger.log(
					f"Skipping default section ({self.__DEFAULT_TARGET_NAME}) because we've already found at least one match: {found_ssh_config_name}"
				)
				continue
			
			# Check the interface
			if (
				# Matches, if current interface found in adapters
				self.__action_interface in target.adapters
				
				# Can also match if we're in the default section
				or target_name == self.__DEFAULT_TARGET_NAME
			):
				pass
			else:
				self.__logger.log(
					f"Target \"{target_name}\" didn't match any interfaces; Skipping"
				)
				continue
			
			# Grab the SSID this adapter is currently connected to
			interface_ssid = self.get_interface_ssid(self.__action_interface)
			if not interface_ssid:
				self.__logger.log(
					f"Interface \"{interface_ssid}\" isn't connected to anything ... "
				)
			self.__logger.log(
				f"Interface \"{self.__action_interface}\" is currently connected to: \"{interface_ssid}\""
			)
			
			# Must also match at least one SSID,
			# OR we're in the default section
			if interface_ssid not in target.ssids and target_name != self.__DEFAULT_TARGET_NAME:
				self.__logger.log(
					f"Did not find SSID \"{interface_ssid}\" in target ssids: " + str(target.ssids)
				)
				continue
			
			# Found a match!
			found_ssh_config_name = target.ssh_config_name
			self.__logger.log(
				f"Found matching ssh config name: {found_ssh_config_name}"
			)
		
		# Didn't find anything? Go default ...
		if not found_ssh_config_name:
			if self.__DEFAULT_TARGET_NAME in self.__config.targets.keys():
				target = self.__config.targets[self.__DEFAULT_TARGET_NAME]
				found_ssh_config_name = target.ssh_config_name
				self.__logger.log(
					f"No matches found; Defaulting to: {found_ssh_config_name}"
				)
		
		return found_ssh_config_name
	
	@staticmethod
	def get_interface_ssid(interface_name):
		
		#
		p = subprocess.Popen(["nmcli", "dev", "show", interface_name], stdout=subprocess.PIPE)
		(stdout, stderr) = p.communicate()
		stdout = stdout.decode()
		
		#
		r = re.compile(
			pattern=r"^GENERAL.CONNECTION:\s+(?P<ssid>[^\s].+)$",
			flags=re.MULTILINE
		)
		match = r.search(stdout)
		
		return match.group("ssid")
