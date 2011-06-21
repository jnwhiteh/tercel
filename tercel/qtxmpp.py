# -*- coding: utf-8 -*-
"""
Qt wrapper around SleekXMPP
"""

from PySide.QtCore import QObject, Signal
from sleekxmpp import ClientXMPP
from .utils import messageToDict


class QXMPPClient(QObject):
	"""
	A Qt XMPP client
	Wrapper around sleekxmpp.ClientXMPP
	"""
	
	messageReceived = Signal(str, dict)
	rosterUpdated = Signal(object)
	
	def __init__(self, username, password, host, port=5222):
		super(QXMPPClient, self).__init__()
		self._stream = ClientXMPP(username, password)
		self._username = username
		self._password = password
		self._host = host
		self._port = port
		# Wrap Qt signals around the sleekxmpp ones
		self._stream.add_event_handler("message", self.__messageReceived)
		self._stream.add_event_handler("roster_update", self.__rosterUpdated)
	
	def __messageReceived(self, message):
		message = messageToDict(message)
		self.messageReceived.emit(message)
	
	def __rosterUpdated(self, roster):
		roster = dict(roster["roster"]["items"])
		self.rosterUpdated.emit(roster)
	
	def connectToHost(self, host):
		self.stream().connect(host)
	
	def host(self):
		return self._host
	
	def password(self):
		return self._password
	
	def port(self):
		return self._port
	
	def username(self):
		return self._username
	
	def waitForProcessEnd(self):
		self.stream().process(threaded=False)
	
	def roster(self):
		return self.stream().roster
	
	def queryRoster(self):
		self.stream().get_roster(block=False)
	
	def stream(self):
		return self._stream

# Remove for production
#import logging
#logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
