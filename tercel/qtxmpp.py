# -*- coding: utf-8 -*-
"""
Qt wrapper around SleekXMPP
"""

from sleekxmpp import ClientXMPP

class QXMPPClient(ClientXMPP):
	def __init__(self, parent=None, *args):
		super(ClientXMPP, self).__init__(*args)
		self._parent = parent
	
	def parent(self):
		return self._parent

# Remove for production
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
