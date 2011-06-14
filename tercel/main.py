# -*- coding: utf-8 -*-
"""
PySide interface for Tercel
"""

from PySide.QtCore import *
from PySide.QtGui import *

class Tercel(QApplication):
	def __init__(self, argv):
		super(Tercel, self).__init__(argv)
		self.mainWindow = MainWindow()

class MainWindow(QMainWindow):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		
		self.tabWidget = QTabWidget()
		self.tabWidget.setDocumentMode(True)
		self.tabWidget.setMovable(True)
		self.tabWidget.setTabsClosable(True)
		self.tabWidget.tabCloseRequested.connect(self.actionCloseTab)
		self.setCentralWidget(self.tabWidget)
		self.actionNewTab()
	
	def actionNewTab(self):
		self.tabWidget.addTab(NewTabWidget(), QIcon.fromTheme("user-online"), "New Tab")
	
	def actionCloseTab(self):
		pass

class NewTabWidget(QWidget):
	pass

def main():
	import signal
	import sys
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = Tercel(sys.argv)
	
	app.mainWindow.show()
	sys.exit(app.exec_())
