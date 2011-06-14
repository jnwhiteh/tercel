# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import QWebView


class Tercel(QApplication):
	def __init__(self, argv):
		super(Tercel, self).__init__(argv)
		self.mainWindow = MainWindow()

class TabWidget(QTabWidget):
	def __init__(self, *args):
		super(TabWidget, self).__init__(*args)
		self.setDocumentMode(True)
		self.setMovable(True)
		self.setTabsClosable(True)

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		self.tabWidget = TabWidget(self)
		self.tabWidget.tabCloseRequested.connect(self.actionCloseTab)
		self.setCentralWidget(self.tabWidget)
		self.actionNewTab()
	
	def actionNewTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
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
	app = Tercel(sys.argv)
	
	app.mainWindow.show()
	sys.exit(app.exec_())
