

from domain.SSHConfigChanger import SSHConfigChanger


import argparse


def main():
	
	parser = argparse.ArgumentParser(
		prog="Mike's SSH Config Changer"
	)
	
	parser.add_argument(
		"--dry-run", "-d",
		dest="dry_run",
		default=False,
		action="store_true",
		help="Pass this flag to print what would be changed, without actually changing anything"
	)
	
	parser.add_argument(
		"--config", "-c",
		dest="config_file",
		required=True,
		help="Specify path to configuration file",
	)
	
	parser.add_argument(
		"--interface", "--action-interface",
		dest="action_interface",
		required=True,
		help="Specify the interface specified by NetworkManager's action"
	)
	
	parser.add_argument(
		"--command", "--action-command",
		dest="action_command",
		required=True,
		help="Specify the command specified by NetworkManager's action"
	)
	
	args = parser.parse_args()
	
	configger = SSHConfigChanger(
		dry_run=args.dry_run,
		action_interface=args.action_interface,
		action_command=args.action_command,
		config_file_path=args.config_file,
	)
	configger.run()


#   Main Entry
if __name__ == "__main__":
	main()

