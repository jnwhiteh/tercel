# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import QWebView
from .qtxmpp import QXMPPClient


class Tercel(QApplication):
	def __init__(self, argv):
		super(Tercel, self).__init__(argv)
		self.mainWindow = MainWindow()
		username, password = argv
		self.xmpp = XMPPClient(self, username, password)

class XMPPConnectionThread(QThread):
	def __init__(self, xmpp, host, *args):
		super(XMPPConnectionThread, self).__init__(*args)
		self.xmpp = xmpp
		self.host = host
	
	def run(self):
		self.xmpp.connect(self.host)
		self.xmpp.process(threaded=False)

class XMPPClient(QXMPPClient):
	def __init__(self, *args):
		super(XMPPClient, self).__init__(*args)
		self.add_event_handler("session_start", self.onConnect)
		self.add_event_handler("message", self.onMessageReceived)
		XMPPConnectionThread(self, ("talk.google.com", 5222), qApp).start()
	
	def onConnect(self, event):
		self.sendPresence("Writing an XMPP client, please do not send messages")
	
	def onMessageReceived(self, message):
		self.sendMessage(message["from"], message["body"])

class TabWidget(QTabWidget):
	def __init__(self, *args):
		super(TabWidget, self).__init__(*args)
		self.setDocumentMode(True)
		self.setMovable(True)
		self.setTabsClosable(True)

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(QIcon.fromTheme("application-exit"), "&Quit", self.close, "Ctrl+Q")
		
		self.tabs = {}
		
		layout = QVBoxLayout(self)
		centralWidget = QWidget(self)
		centralWidget.setLayout(layout)
		self.setCentralWidget(centralWidget)
		
		self.tabWidget = TabWidget(self)
		self.tabWidget.tabCloseRequested.connect(self.actionCloseTab)
		layout.addWidget(self.tabWidget)
		
		self.textbox = QTextEdit(self)
		layout.addWidget(self.textbox)
		
		self.actionNewTab()
		self.actionOpenToContact("account", "adys.wh@gmail.com")
	
	def actionNewTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
	def actionOpenToContact(self, account, address):
		internalAddress = "tercel://contact/%s/%s/" % (account, address)
		if internalAddress not in self.tabs:
			widget = QWebView()
			widget.load("http://example.com")
			self.tabs[internalAddress] = widget
		
		self.tabWidget.addTab(widget, QIcon.fromTheme("user-online"), address)
	
	def actionCloseTab(self):
		pass

class NewTabWidget(QWebView):
	def __init__(self, *args):
		super(NewTabWidget, self).__init__(*args)
		self.load("http://google.com")

def main():
	import signal
	import sys
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = Tercel(sys.argv[1:])
	
	app.mainWindow.show()
	sys.exit(app.exec_())
