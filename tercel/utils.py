# -*- coding: utf-8 -*-
"""
Util functions
"""

from time import strftime


def messageToDict(message):
	message = dict(message)
	message["from_resource"] = message["from"].resource
	message["from"] = message["from"].bare
	message["to_resource"] = message["to"].resource
	message["to"] = message["to"].bare
	message["timestamp"] = strftime("[%H:%M:%S]")
	return message
