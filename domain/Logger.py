

import sys
import syslog


class Logger:
	
	@staticmethod
	def log(s):
		
		print("[SSHConfiger]", s)
		syslog.syslog("[SSHConfiger] " + s)
	
	#
	@staticmethod
	def complain(s):
		
		syslog.syslog(syslog.LOG_ERR, "[SSHConfiger] " + s)
		print("[SSHConfiger]", s, file=sys.stderr)
