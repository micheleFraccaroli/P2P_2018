import sys
import os
from time import sleep
import string
import random

class Vicini:
	def __init__(self,config):

		# Per 16 volte scelgo un char casuale tra lower_case, upper_case o digit
		rand=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
		self.pack='NEAR'+rand+config.selfV4+config.selfV6+config.selfP+config.ttl

	def cercaVicini(self,config):


	