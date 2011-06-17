# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

import json
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
		self.mainWindow.newTab()

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
		self.connect_("session_start", self.start)
		self.connect_("message", self.parent().mainWindow.messageReceived)
		XMPPConnectionThread(self, ("talk.google.com", 5222), qApp).start()
	
	def start(self, event):
		self.sendPresence(pshow="Writing an XMPP client, please do not send messages")
		self.queryRoster()

class TabWidget(QTabWidget):
	tabOpenRequested = Signal(object, object)
	messageReceived = Signal(object)
	
	def __init__(self, *args):
		super(TabWidget, self).__init__(*args)
		self.tabs = {}
		self.setDocumentMode(True)
		self.setMovable(True)
		self.setTabsClosable(True)
		self.tabOpenRequested.connect(self.actionOpenToContact)
		# hack? Because of threading issues, we seem to have to callback like that...
		self.messageReceived.connect(lambda func: func())
	
	def actionOpenToContact(self, message, callback):
		if message in self.tabs:
			# open to that tab
			return
		layout = QVBoxLayout()
		widget = QWidget(self)
		widget.setLayout(layout)
		widget.webView = QWebView()
		widget.webView.load("file:///home/adys/src/git/tercel/tercel/res/tab.html")
		layout.addWidget(widget.webView)
		widget.textEdit = TextEdit()
		layout.addWidget(widget.textEdit)
		widget.message = message
		self.tabs[message["to"].full] = widget
		widget.webView.loadFinished.connect(callback)
		self.addTab(widget, QIcon.fromTheme("user-online"), widget.message["from"].full)

class TextEdit(QTextEdit):
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
			if e.modifiers() & (Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier):
				self.insertPlainText("\n")
			else:
				self.sendMessage()
			return
		super(TextEdit, self).keyPressEvent(e)
	
	def sendMessage(self):
		recipient = self.parent().parent().parent().currentWidget().message["from"]
		qApp.xmpp.sendMessage(recipient, self.toPlainText())
		self.clear()

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(QIcon.fromTheme("window-new"), "&New Tab", self.newTab, "Ctrl+T")
		fileMenu.addAction(QIcon.fromTheme("window-close"), "&Close Tab", self.closeTab, "Ctrl+W")
		fileMenu.addAction(QIcon.fromTheme("application-exit"), "&Quit", self.close, "Ctrl+Q")
		
		layout = QVBoxLayout()
		centralWidget = QWidget(self)
		centralWidget.setLayout(layout)
		self.setCentralWidget(centralWidget)
		
		self.tabWidget = TabWidget()
		self.tabWidget.tabCloseRequested.connect(self.closeTab)
		layout.addWidget(self.tabWidget)
	
	def newTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
	def messageReceived(self, message):
		if message["to"].full not in self.tabWidget.tabs:
			# We need a different method here, because we need to wait for page load
			self.tabWidget.tabOpenRequested.emit(message, lambda: self.onMessageReceived(message))
		else:
			self.tabWidget.messageReceived.emit(lambda: self.onMessageReceived(message))
	
	def onMessageReceived(self, message):
		date = strftime("[%H:%M:%S]")
		source = "newMessage(%r, %r, %r, %r)" % (date, message["from"].full, message["body"], 1)
		frame = self.tabWidget.tabs[message["to"].full].webView.page().currentFrame()
		frame.evaluateJavaScript(source)
	
	def closeTab(self):
		self.tabWidget.removeTab(self.tabWidget.currentIndex())

class NewTabWidget(QWebView):
	def __init__(self, *args):
		super(NewTabWidget, self).__init__(*args)
		self.load("file:///home/adys/src/git/tercel/tercel/res/new-tab.html")
		
		def loadRoster():
			# blocker?
			qApp.xmpp.queryRoster()
			self.updateRoster(qApp.xmpp.roster)
		self.loadFinished.connect(loadRoster)
	
	def updateRoster(self, roster):
		self.page().currentFrame().evaluateJavaScript("updateRoster(%s)" % (json.dumps(roster)))

def main():
	import signal
	import sys
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = Tercel(sys.argv[1:])
	
	app.mainWindow.show()
	sys.exit(app.exec_())
