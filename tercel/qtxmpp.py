# -*- coding: utf-8 -*-
"""
Qt wrapper around SleekXMPP
"""

from PySide.QtCore import QObject, Signal
from sleekxmpp import ClientXMPP
from .utils import messageToDict


class QXmppClient(QObject):
	"""
	A Qt XMPP client
	Wrapper around sleekxmpp.ClientXMPP
	"""
	
	messageReceived = Signal(dict)
	rosterUpdated = Signal(str, object)
	#messageSent = Signal(dict)
	
	def __init__(self, username, password, host, port=5222, parent=None):
		super(QXmppClient, self).__init__(parent)
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
	
	def __rosterUpdated(self, iq):
		roster = dict(iq["roster"]["items"])
		account = str(iq["to"].bare)
		self.rosterUpdated.emit(account, roster)
	
	def connectToHost(self, host):
		self.stream().connect(host)
	
	def host(self):
		return self._host
	
	def password(self):
		return self._password
	
	def port(self):
		return self._port
	
	def queryRoster(self):
		self.stream().get_roster(block=False)
	
	def roster(self):
		return self.stream().roster
	
	def sendMessage(self, contact, message):
		message = self.stream().make_message(contact, message)
		message.send()
		return messageToDict(message)
	
	def stream(self):
		return self._stream
	
	def username(self):
		return self._username
	
	def waitForProcessEnd(self):
		self.stream().process(threaded=False)

class QXmppMessage(QObject):
	"""
	An XMPP message
	Parent should be a QXmppClient instance
	"""
	
	def __init__(self, body, parent=None):
		super(QXmppClient, self).__init__(parent)
		self._body = body
	
	def body(self):
		return self._body

class QXmppUser(QObject):
	"""
	An XMPP user
	Parent should be a QXmppClient instance
	"""
	
	messageReceived = Signal(dict)
	messageSent = Signal(dict)
	
	def __init__(self, jabberId, parent=None):
		super(QXmppClient, self).__init__(parent)
		self._jabberId = jabberId
	
	def jabberId(self):
		return self._jabberId
	
	def sendMessage(self, body):
		message = QXmppMessage(body, self.parent())
		self.parent().stream().make_message(self.jabberID(), body).send()

# Remove for production
#import logging
#logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
