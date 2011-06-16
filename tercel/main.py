# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

from time import strftime
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
		self.connect_("session_start", self.onConnect)
		self.connect_("message", self.parent().mainWindow.messageReceived)
		XMPPConnectionThread(self, ("talk.google.com", 5222), qApp).start()
	
	def onConnect(self, event):
		self.sendPresence("Writing an XMPP client, please do not send messages")

class TabWidget(QTabWidget):
	tabOpenRequested = Signal(str, str, object)
	
	def __init__(self, *args):
		super(TabWidget, self).__init__(*args)
		self.tabs = {}
		self.setDocumentMode(True)
		self.setMovable(True)
		self.setTabsClosable(True)
		self.tabOpenRequested.connect(self.actionOpenToContact)
	
	def actionOpenToContact(self, account, address, callback):
		#internalAddress = "tercel://contact/%s/%s/" % (account, address)
		internalAddress = address
		if internalAddress not in self.tabs:
			widget = QWebView()
			widget.load("file:///home/adys/src/git/tercel/tercel/res/tab.html")
			self.tabs[internalAddress] = widget
		self.addTab(widget, QIcon.fromTheme("user-online"), "address")
		widget.loadFinished.connect(callback)

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(QIcon.fromTheme("application-exit"), "&Quit", self.close, "Ctrl+Q")
		
		layout = QVBoxLayout()
		centralWidget = QWidget(self)
		centralWidget.setLayout(layout)
		self.setCentralWidget(centralWidget)
		
		self.tabWidget = TabWidget(self)
		self.tabWidget.tabCloseRequested.connect(self.actionCloseTab)
		layout.addWidget(self.tabWidget)
		
		self.textbox = QTextEdit(self)
		layout.addWidget(self.textbox)
		
		self.actionNewTab()
	
	def actionNewTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
	def messageReceived(self, message):
		to = message["to"].full
		from_ = message["from"].full
		if to not in self.tabWidget.tabs:
			self.tabWidget.tabOpenRequested.emit(from_, to, lambda: self.sendMessage(from_, to, message["body"]))
	
	def sendMessage(self, sender, recipient, message):
		date = strftime("[%H:%M:%S]")
		source = "newMessage(%r, %r, %r, %r);" % (date, sender, message, 1)
		frame = self.tabWidget.tabs[recipient].page().currentFrame()
		frame.evaluateJavaScript(source)
	
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
