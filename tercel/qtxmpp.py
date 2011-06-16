# -*- coding: utf-8 -*-
"""
Qt wrapper around SleekXMPP
"""

from sleekxmpp import ClientXMPP

class QXMPPClient(ClientXMPP):
	def __init__(self, parent=None, *args):
		super(QXMPPClient, self).__init__(*args)
		self._parent = parent
	
	def connect_(self, event, callback):
		self.add_event_handler(event, callback)
	
	def parent(self):
		return self._parent
	
	def queryRoster(self):
		self.get_roster()

# Remove for production
#import logging
#logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
