

from domain.Logger import Logger


import os
from pathlib import Path
import yaml


class Target:
	
	def __init__(self, logger: Logger, name):
		
		self.__logger = logger
		
		self.__name = name
		self.__data = {}
		
		self.__adapters_names = []
		self.__ssids = []
		
		# noinspection PyTypeChecker
		self.__ssh_config_file_name: str = None
	
	def __str__(self):
		
		s = ""
		
		s += f"Target: {self.__name}"
		s += f"\n> SSH config file name: {self.__ssh_config_file_name}"
		s += f"\n> Adapters: "

		if len(self.__adapters_names) > 0:
			s += ", ".join(self.__adapters_names)
		else:
			s += "[none]"
		s += f"\n> SSIDs: "

		if len(self.__ssids) > 0:
			s += ", ".join(self.__ssids)
		else:
			s += "[none]"
		
		return s
	
	def log(self, s):
	
		self.__logger.log(
			f"[Target::{self.__name}] {s}"
		)
	
	def complain(self, s):
		
		self.__logger.complain(
			f"[Target::{self.__name}] {s}"
		)
		
	def consume_data(self, data: dict):
		
		assert isinstance(data, dict), (
			f"Data should be a dict (found: {type(data).__name__}) "
		)
		
		self.__data = data
		
		assert "config-file-name" in self.__data.keys(), (
			f"Name of ssh config file must be present at config-file-name"
		)
		config_file_name = self.__data["config-file-name"]
		assert isinstance(config_file_name, str), (
			f"config-file-name must be a string, but got: {type(config_file_name).__name__}"
		)
		self.__ssh_config_file_name = config_file_name
		
		if "adapters" in self.__data.keys():
			adapters = self.__data["adapters"]
			if isinstance(adapters, list):
				pass
			elif isinstance(adapters, str):
				adapters = [adapters]
			else:
				raise AssertionError(f"Unsupported adapters data type: {type(adapters).__name__}")
			self.__adapters_names.extend(adapters)
		
		if "adapter" in self.__data.keys():
			adapters = self.__data["adapter"]
			if isinstance(adapters, list):
				pass
			elif isinstance(adapters, str):
				adapters = [adapters]
			else:
				raise AssertionError(f"Unsupported adapter data type: {type(adapters).__name__}")
			self.__adapters_names.extend(adapters)
		
		if "ssids" in self.__data.keys():
			ssids = self.__data["ssids"]
			if isinstance(ssids, list):
				pass
			elif isinstance(ssids, str):
				ssids = [ssids]
			else:
				raise AssertionError(f"Unsupported ssids data type: {type(ssids).__name__}")
			self.__ssids.extend(ssids)
			
		if "ssid" in self.__data.keys():
			ssids = self.__data["ssid"]
			if isinstance(ssids, list):
				pass
			elif isinstance(ssids, str):
				ssids = [ssids]
			else:
				raise AssertionError(f"Unsupported ssid data type: {type(ssids).__name__}")
			self.__ssids.extend(ssids)
		
		assert len(self.__adapters_names) > 0, (
			f"At least one adapter must be configured at target-name::adapters"
		)
	
	@property
	def name(self) -> str:
		return self.__name
	
	@property
	def ssh_config_file_name(self) -> str:
		return self.__ssh_config_file_name
	
	@property
	def adapters(self) -> list[str]:
		return self.__adapters_names
	
	@property
	def ssids(self) -> list[str]:
		return self.__ssids


class Config:
	
	__DEFAULT_NORMAL_SSH_CONFIG_FILE_NAME = "config"
	__DEFAULT_SSH_DIRECTORY_NAME = ".ssh"
	
	def __init__(self, logger: Logger, file_path: str):
		
		self.__logger = logger
		
		if isinstance(file_path, str):
			file_path = Path(file_path)
		elif isinstance(file_path, Path):
			pass
		else:
			raise AssertionError("File path should be a string or Path object")
		
		self.__file_path = file_path
		
		self.__data = {}
		
		self.__dry_run = False
		self.__ssh_dir = Path(os.path.expanduser("~")) / self.__DEFAULT_SSH_DIRECTORY_NAME
		# noinspection PyTypeChecker
		self.__default_target_name: str = None
		self.__targets = {}
		
		self._load_config()
		self._consume_config()
		
		print(self)
	
	def __str__(self):
		
		s = ""
		
		s += "*** Config ***"
		s += "\n Dry run: " + "True" if self.__dry_run else "False"
		for target in self.__targets.values():
			s += "\n" + str(target)
		
		return s
	
	def _load_config(self):
		
		assert self.__file_path.exists(), "Config file must exist"
		
		with open(self.__file_path) as f:
			
			self.__data = yaml.safe_load(f)
	
	def _consume_config(self):
		
		assert isinstance(self.__data, dict), (
			f"Config data must be a dict"
		)
		
		assert "options" in self.__data.keys(), (
			f"Options key missing from config"
		)
		options = self.__data["options"]
		assert isinstance(options, dict), "Config options must be a dict!"
		
		if "dry-run" in options.keys():
			d = options["dry-run"]
			assert isinstance(d, bool), "options::dry-run must be a bool"
			if d:
				self.__logger.complain(f"Dry run enabled in config")
			self.__dry_run = d
		
		if "ssh-dir" in options.keys():
			ssh_dir = Path(options["ssh-dir"])
			assert ssh_dir.exists(), f"options::ssh-dir must be a valid directory"
			self.__ssh_dir = ssh_dir
			self.__logger.log(f"Found ssh dir: {self.__ssh_dir}")
		else:
			self.__logger.log(f"options::ssh-dir not found")
		
		assert "default-target" in options.keys(), (
			f"Must specify the name of the default target at options::default-target"
		)
		default_target_name = options["default-target"]
		assert isinstance(default_target_name, str), (
			f"Default target name must be a string but got: {type(default_target_name).__name__}"
		)
		self.__default_target_name = default_target_name
		
		self.__targets = {}
		
		assert "targets" in self.__data.keys(), "Config should specify targets"
		targets = self.__data["targets"]
		assert isinstance(targets, dict), "Targets should be a dict, where each key is one target"
		for target_name in targets.keys():
			
			self.__logger.log(f"Parsing target: {target_name}")
			
			try:
				t = Target(
					logger=self.__logger,
					name=target_name,
				)
				t.consume_data(data=targets[target_name])
			except AssertionError as e:
				self.__logger.complain(
					f"Failed to parse target \"{target_name}\""
					f"\n{e}"
				)
				raise e
			
			self.__targets[target_name] = t
		
		if self.__default_target_name not in self.__targets.keys():
			raise AssertionError(
				f"Default target specified as {self.__default_target_name} but was not found in dict of targets"
			)
	
	@property
	def default_normal_ssh_config_file_name(self) -> str:
		return self.__DEFAULT_NORMAL_SSH_CONFIG_FILE_NAME
	
	@property
	def file_path(self) -> Path:
		return self.__file_path
	
	@property
	def dry_run(self) -> bool:
		return self.__dry_run
	
	@dry_run.setter
	def dry_run(self, b: bool):
		self.__dry_run = b
	
	@property
	def default_target_name(self) -> str:
		return self.__default_target_name
	
	@property
	def ssh_dir(self) -> Path | None:
		return self.__ssh_dir
	
	@property
	def targets(self) -> [Target]:
		return self.__targets
