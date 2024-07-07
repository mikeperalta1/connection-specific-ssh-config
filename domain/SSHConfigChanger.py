

from domain.config.Config import Config
from domain.config.Config import Target
from domain.Logger import Logger


import os
from pathlib import Path
import re
import subprocess
import sys


class SSHConfigChanger:
	
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
		ssh_config_target = self.determine_ssh_config_target()
		if ssh_config_target is None:
			self.die("Unable to determine appropriate ssh config name; Quitting")
		self.__logger.log(
			f"Determined ssh config name: {ssh_config_target.name}"
		)
		
		# Make paths
		ssh_config_path_link = self.__config.ssh_dir / self.__config.default_normal_ssh_config_file_name
		ssh_config_path_target = self.__config.ssh_dir / ssh_config_target.ssh_config_file_name
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
	def require_symlink_or_none(self, file_path: Path):
		
		if file_path.is_file() and file_path.exists() and not file_path.is_symlink():
			self.die(
				f"For safety, refusing to continue because the target ssh config file exists and is not a symlink:"
				f" {file_path}"
			)
	
	def determine_ssh_config_target(self) -> Target:
		
		#
		self.__logger.log("Attempting to determine SSH config name")
		
		# Start off by assuming the default target
		# noinspection PyTypeChecker
		selected_target = None
		selected_target: Target
		
		# Check each section
		for target_name in self.__config.targets:
			
			self.__logger.log(f"Examining target: {target_name}")
			
			if selected_target is not None and target_name == selected_target.name:
				self.__logger.log(f"Ignoring target because it is already selected: {target_name}")
				continue
			
			target = self.__config.targets[target_name]
			
			# Matches, if current interface found in adapters
			if self.__action_interface not in target.adapters:
				self.__logger.log(
					f"Target \"{target_name}\" didn't match any interfaces; Skipping"
				)
				continue
			
			# Grab the SSID this adapter is currently connected to
			interface_ssid = self.get_interface_ssid(self.__action_interface)
			if not interface_ssid:
				self.__logger.log(
					f"Interface \"{interface_ssid}\" isn't connected to anything; Done looking"
				)
				break
			self.__logger.log(
				f"Interface \"{self.__action_interface}\" is currently connected to: \"{interface_ssid}\""
			)
			
			# Must also match at least one SSID
			if interface_ssid in target.ssids:
				
				self.__logger.log(
					f"Found SSID \"{interface_ssid}\" in target {target_name}"
				)
				
				# Only override selected target if this one has less SSIDs,
				# or there is no currently selected target
				if selected_target is None:
					self.__logger.log(
						f"Found first suitable target: {target_name}"
					)
					selected_target = target
				if len(target.ssids) < len(selected_target.ssids):
					self.__logger.log(
						f"Target \"{target_name}\""
						f" seems to be a better match than \"{selected_target.name}\""
						f" because it has fewer specified SSIDs"
						f" ({len(target.ssids)} vs. {len(selected_target.ssids)})"
					)
					selected_target = target
		
		if selected_target is None:
			selected_target = self.__config.targets[self.__config.default_target_name]
			self.__logger.log(f"No suitable target found; Defaulting to: {selected_target.name}")
		
		return selected_target
	
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
