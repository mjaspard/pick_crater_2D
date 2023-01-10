from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, \
QSpacerItem
from PyQt5.QtCore import QMetaObject, pyqtSlot

class MainWindowPickApp(QMainWindow):   
	def __init__(self): 
		super(MainWindowPickApp,self).__init__() 
		self.resize(300,150) 
		self.setWindowTitle("SAR Picking App")   
		self.centralWidget = QWidget(self) 
		self.setCentralWidget(self.centralWidget) 
		self.label = QLabel("Titre",self.centralWidget)   
		self.lineEditTitre = QLineEdit(self.centralWidget) 
		self.pushButtonOK = QPushButton("OK",self.centralWidget) 

		self.hBoxLayout = QHBoxLayout()
		self.hBoxLayout.addWidget(self.label)
		self.hBoxLayout.addWidget(self.lineEditTitre)
		self.hBoxLayout2 = QHBoxLayout()
		self.hBoxLayout2.addStretch()
		self.hBoxLayout2.addWidget(self.pushButtonOK)
		self.hBoxLayout2.addStretch()
		
		self.vBoxLayout = QVBoxLayout(self.centralWidget)
		self.vBoxLayout.addLayout(self.hBoxLayout)
		self.vBoxLayout.addStretch()
		self.vBoxLayout.addLayout(self.hBoxLayout2)
		

		self.pushButtonOK.setObjectName("pushButton3OK")							# slot solution1
		QMetaObject.connectSlotsByName(self)									# slot solution1
# 		self.pushButtonOK.clicked.connect(self.onPushButtonOKClicked) 			# slot solution2
		
		
# 	def onPushButtonOKClicked(self): 													# slot solution2
# 		QMessageBox.information(self,"Info", "Titre : "+self.lineEditTitre.text())		# slot solution2
		
	@pyqtSlot() 																		# slot solution1			
	def on_pushButton3OK_clicked(self):													# slot solution1
		QMessageBox.information(self,"Info2", "Titre2 : "+self.lineEditTitre.text())	# slot solution1