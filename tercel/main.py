# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

import json
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import QWebView, QWebPage
from .qtxmpp import QXMPPClient


class Tercel(QApplication):
	def __init__(self, argv):
		super(Tercel, self).__init__(argv)
		self.setApplicationName("tercel")
		self.setOrganizationName("tercel")
		self.settings = QSettings()
		self.settings.setPath(QSettings.IniFormat, QSettings.UserScope, "tercel")
		self.mainWindow = MainWindow()
		self.populateAccounts()
		self.mainWindow.newTab()
	
	def openUrl(self, url):
		if url.scheme() == "tercel":
			address = url.path()[1:]
			self.mainWindow.tabWidget.tabOpenRequested.emit(address)
	
	def populateAccounts(self):
		settings = self.settings
		self.accounts = {}
		size = settings.beginReadArray("logins")
		for i in range(size):
			settings.setArrayIndex(i)
			username = settings.value("username")
			client = XMPPClient(username, settings.value("password"))
			host = settings.value("host")
			port = int(settings.value("port"))
			client.start(host, port)
			self.accounts[username] = client
		
		settings.endArray()

class ConnectionThread(QThread):
	def __init__(self, client, host, *args):
		super(ConnectionThread, self).__init__(*args)
		self.client = client
		self.host = host
	
	def run(self):
		self.client.connectToHost(self.host)
		self.client.waitForProcessEnd()

class XMPPClient(QXMPPClient):
	def start(self, host, port):
		ConnectionThread(self, (host, port), qApp).start()
		self.messageReceived.connect(qApp.mainWindow.messageReceived)
		#self.sendPresence(pshow="Writing an XMPP client, please do not send messages")

class TabWidget(QTabWidget):
	tabOpenRequested = Signal(str)
	messageReceived = Signal(str, dict)
	
	def __init__(self, *args):
		super(TabWidget, self).__init__(*args)
		self.tabs = {}
		self.setDocumentMode(True)
		self.setMovable(True)
		self.setTabsClosable(True)
		self.tabOpenRequested.connect(self.onTabOpenRequested)
		self.messageReceived.connect(self.onMessageReceived)
	
	def closeTab(self, index):
		widget = self.widget(index)
		if hasattr(widget, "contact"):
			del self.tabs[widget.contact]
		del widget
		self.removeTab(index)
	
	def onTabOpenRequested(self, contact):
		if contact in self.tabs:
			self.setCurrentContact(contact)
			return
		
		# Build the tab
		layout = QVBoxLayout()
		widget = QWidget(self)
		widget.setLayout(layout)
		widget.contact = contact
		self.tabs[contact] = widget
		
		widget.webView = QWebView()
		widget.webView.isLoaded = False
		widget.webView.loadFinished.connect(lambda: setattr(widget.webView, "isLoaded", True))
		widget.webView.linkClicked.connect(qApp.openUrl)
		widget.webView.load("file:///home/adys/src/git/tercel/tercel/res/tab.html")
		layout.addWidget(widget.webView)
		
		widget.textEdit = TextEdit()
		layout.addWidget(widget.textEdit)
		
		self.addTab(widget, QIcon.fromTheme("user-online"), contact)
		self.setCurrentContact(contact)
		widget.textEdit.setFocus(Qt.OtherFocusReason)
	
	def onMessageReceived(self, contact, message):
		source = "newMessage(%s)" % (json.dumps(message))
		webView = self.tabs[contact].webView
		# Check if the page is loaded yet, otherwise evaluateJavaScript doesn't do anything
		if webView.isLoaded:
			webView.page().currentFrame().evaluateJavaScript(source)
		else:
			webView.loadFinished.connect(lambda: webView.page().currentFrame().evaluateJavaScript(source))
	
	def setCurrentContact(self, contact):
		#if contact in self.tabs:
		self.setCurrentIndex(self.indexOf(self.tabs[contact]))

class TextEdit(QTextEdit):
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
			if event.modifiers() & (Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier):
				self.insertPlainText("\n")
			else:
				# widget: self, widget, layout, tabwidget, currentwidget
				widget = self.parent().parent().parent().currentWidget()
				qApp.mainWindow.sendMessage(widget.contact, self.toPlainText())
				self.clear()
			return
		super(TextEdit, self).keyPressEvent(event)

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		layout = QVBoxLayout()
		centralWidget = QWidget(self)
		centralWidget.setLayout(layout)
		self.setCentralWidget(centralWidget)
		
		self.tabWidget = TabWidget()
		self.tabWidget.tabCloseRequested.connect(self.tabWidget.closeTab)
		layout.addWidget(self.tabWidget)
		
		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(QIcon.fromTheme("window-new"), "&New Tab", self.newTab, "Ctrl+T")
		fileMenu.addAction(QIcon.fromTheme("window-close"), "&Close Tab", lambda: self.tabWidget.closeTab(self.tabWidget.currentIndex()), "Ctrl+W")
		fileMenu.addAction(QIcon.fromTheme("application-exit"), "&Quit", self.close, "Ctrl+Q")
		
		aboutMenu = self.menuBar().addMenu("&Help")
		aboutMenu.addAction(QIcon.fromTheme("help-about"), "&About", lambda: QDesktopServices.openUrl("https://github.com/adys/tercel/"))
		
		self.readSettings()
	
	def closeEvent(self, event):
		self.writeSettings()
		event.accept()
	
	def messageReceived(self, message):
		if message["from"] not in self.tabWidget.tabs:
			self.tabWidget.tabOpenRequested.emit(message["from"])
		
		self.tabWidget.messageReceived.emit(message["from"], message)
	
	def newTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
	def readSettings(self):
		settings = qApp.settings
		settings.beginGroup("MainWindow")
		self.resize(settings.value("size", QSize(400, 400)))
		self.move(settings.value("pos", QPoint(200, 200)))
		if settings.value("maximized", "false") == "true": # http://lists.pyside.org/pipermail/pyside/2011-April/002401.html
			self.showMaximized()
		settings.endGroup()
	
	def sendMessage(self, contact, body):
		frame = self.tabWidget.tabs[contact].webView.page().currentFrame()
		message = qApp.xmpp.make_message(contact, body)
		message.send()
		self.tabWidget.messageReceived.emit(contact, messageToDict(message))
	
	def writeSettings(self):
		settings = qApp.settings
		settings.beginGroup("MainWindow")
		settings.setValue("size", self.size())
		settings.setValue("pos", self.pos())
		settings.setValue("maximized", self.isMaximized())
		settings.endGroup()

class NewTabWidget(QWebView):
	def __init__(self, *args):
		super(NewTabWidget, self).__init__(*args)
		self.load("file:///home/adys/src/git/tercel/tercel/res/new-tab.html")
		
		self.loadFinished.connect(self.loadRoster)
		self.linkClicked.connect(qApp.openUrl)
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
	
	def loadRoster(self):
		for account in qApp.accounts.values():
			account.queryRoster()
			account.rosterUpdated.connect(self.updateRoster)
	
	def updateRoster(self, roster):
		# XXX laggy
		self.page().currentFrame().evaluateJavaScript("updateRoster(%s)" % (json.dumps(roster)))

def main():
	import signal
	import sys
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = Tercel(sys.argv[1:])
	
	app.mainWindow.show()
	sys.exit(app.exec_())
