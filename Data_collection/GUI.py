'''
This code implements a GUI to collect and save the data from the accelerometer.
The aim is to make the protocol easier for an user. 
We had to sample an accelerometer for 3 minutes while a persone is sleeping in different positions. 
The user must connect to a port (it is possible also to disconnect from this port and change it or rescan the ports). 
Then the user must choose the position of the person and then start sampling. 
After 3 minutes the sampling stops and a '.csv' is saved in the folder automatically in a folder. 
'''

#import the libraries
from re import M
import sys
from time import sleep
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox, 
)
import numpy as np 
import serial 
import pandas as pd
import serial.tools.list_ports
import os
import natsort
from natsort import natsorted

serial_ports = [
        p.name
        for p in serial.tools.list_ports.comports()
    ]

posizioni=['supine','lateral R', 'lateral L','prone']

CONN_STATUS=False

# Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    seriale=serial.Serial()
    stop = pyqtSignal()
    posizione=""


    def run(self):
        """Sampling task. In this part of the code the sampling is done. In the beginning we send a START signal, 
        then we collect all the data coming from the accelerometer and we save them 
        In the end a '.csv' file is saved automatically """

        path1='./raw_data'
        files = [f for f in os.listdir(path1) if not f.startswith('.')]
        files = natsorted(files)
        ##m is used to save the .csv file with a different name
        m=len(files)
        
        fs=50 # sampling frequencies
        min=3 # minutes of registrazion

        count=0
        #We use df to store the data
        df=np.zeros((fs*min*60,3))
        df[:,:]=0
        pos=self.posizione

        # write a string in the serial port to start the sampling
        if (count==0): 

            self.seriale.write(b'a')


        while (count<=fs*min*60):

            if(self.stop==1):
                self.progress.emit(9001)
                self.stop=0
                self.finished.emit()
                return
    
            else:

                data=self.seriale.readline()
                data=str(data, 'utf-8')
                xyz_string_triplet = data.split(",")

                #we save X,Y,Z in different columns
                df[count,0] = int(xyz_string_triplet[0])
                df[count,1] = int(xyz_string_triplet[1])
                df[count,2] = int(xyz_string_triplet[2])
                count=count+1
                self.progress.emit(count)

                if(count==fs*min*60):
                    #When the sampling is done we save all the data labelled in the dataframe
                    data2 = {'X': df[:,0], 'Y':df[:,1], 'Z':df[:,2], 'pos': pos}
                    df2=pd.DataFrame(data2)
                    df2.to_csv(path1+'\example'+str(m)+'.csv', index=False, header=True)
                    df[:,:]=0
                    self.progress.emit(count+1)
                    count=0
                    self.finished.emit()
                    return
                
        

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        '''Set up of the interface'''
        self.setWindowTitle("app")
        self.resize(300, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.combo=QComboBox(self)
        self.combo.addItems(serial_ports)
        self.rescanbt=QPushButton('rescan port')
        self.rescanbt.clicked.connect(self.rescan)
        self.posi=QComboBox(self)
        self.posi.addItems(posizioni)
        self.posi.setDisabled(True)
        self.content = self.combo.currentText()
        self.Label = QLabel("Connect to a port, then choose the position and start sampling")
        self.Label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.connectbt = QPushButton("Connect!", self)
        self.connectbt.clicked.connect(self.Connect)
        self.Startbt = QPushButton("Start sampling!", self)
        self.Startbt.clicked.connect(self.runLongTask)
        self.Startbt.setDisabled(True)
        self.Stopbt=QPushButton("Stop sampling", self)
        self.Stopbt.clicked.connect(self.stopsampling)
        self.Stopbt.setDisabled(True)
        self.flag=0

        # creating a timer object
        self.timer = QTimer(self)
        # update the timer every second
        self.timer.start(1000)
        current_time = QTime.currentTime()
        self.timer.timeout.connect(self.showTime)
        # converting QTime object to string
        label_time = current_time.toString('hh:mm:ss')
        # showing it to the label
        self.label.setText(label_time)

        # Set the layout
        layout1=QHBoxLayout()
        layout1.addWidget(self.rescanbt)
        layout1.addWidget(self.connectbt)

        layout2=QHBoxLayout()
        layout2.addWidget(self.Stopbt)
        layout2.addWidget(self.Startbt)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Label)
        layout.addWidget(self.combo)
        layout.addLayout(layout1)
        layout.addStretch()
        layout.addWidget(self.posi)
        layout.addLayout(layout2)
        self.centralWidget.setLayout(layout)
    

    def stopsampling(self):
        '''This function stops the sampling'''
        self.ser.write(b'b')
        self.Startbt.setEnabled(True)
        self.connectbt.setEnabled(True)
        self.posi.setEnabled(True)
        self.worker.stop=1

    def Connect(self):
        '''This function allow us to connect to a port'''
        global CONN_STATUS
        self.content = self.combo.currentText()

        if(CONN_STATUS==False):
            try: 
                self.ser=serial.Serial(self.content,115200)

                if self.ser.is_open:   
                    self.Label.setText('Connected to the port')
                    CONN_STATUS = True
                    self.Startbt.setDisabled(False)
                    self.Stopbt.setDisabled(False)
                    self.posi.setDisabled(False)
                    self.combo.setDisabled(True)
                    self.rescanbt.setDisabled(True)
                    self.connectbt.setText('Disconnect')
                    self.connectbt.clicked.disconnect()
                    self.connectbt.clicked.connect(self.Disconnect)
                    return

            except serial.SerialException:
                CONN_STATUS=False
                self.Label.setText('The port is not available')
                return
                

    def Disconnect(self): 
        '''this function allows us to disconnect to the port'''
        global CONN_STATUS
        self.ser.close()
        self.connectbt.clicked.disconnect()
        self.connectbt.clicked.connect(self.Connect)
        CONN_STATUS=False
        self.setupUi()
        return
        
    
    def showTime(self):
        '''this function shows the current time'''
        # getting current time
        current_time = QTime.currentTime()
        # # converting QTime object to string
        label_time = current_time.toString('hh:mm:ss')
        # showing it to the label
        self.label.setText(label_time)
  
    def runLongTask(self):
        '''in this function we send the signals to the thread'''
        #We disable the button to avoid double click
        self.Startbt.setEnabled(False)
        self.posi.setDisabled(True)
        ##It's not possible do disconnect to the port while sampling. We have to stop the sampling and then disconnect
        self.connectbt.setDisabled(True) 

        # Create a QThread object
        self.thread = QThread(parent=self)
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        ##Started signal
        self.thread.started.connect(self.worker.run)

        ## Finished signal
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.resampling)
        ##Progress signal
        self.worker.progress.connect(self.reportProgress)
        ## We need to send also the port and the position
        self.worker.seriale=self.ser
        posizione=self.posi.currentText()
        self.worker.posizione=posizione
        self.worker.stop=0

        

        ## We show the moment in which the sampling starts
        self.timer.start(1000)
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.Label.setText('started at:'+ label_time)
        self.Startbt.setText('I am sampling!')
    

        # Start the thread
        self.thread.start()

        #Final resets

        self.thread.finished.connect(

            lambda: self.Startbt.setEnabled(True)
        )


    def reportProgress(self, n):
        '''this function allows us to keep track of the progress of the sampling'''

        p=(100*n)/9000
        p=int(p)
        self.Startbt.setText(f"I am sampling! Done: {p}%")

        if (n==9001): 
            self.Startbt.setText("Click for new sampling")
    


    def resampling(self):
        self.posi.setEnabled(True)
        self.connectbt.setEnabled(True)
        self.Label.setText('The sampling is finished. You can start another sampling')

    def rescan (self):
        '''function to rescan the ports'''
        serial_ports=[]
        serial_ports = [
        p.name
        for p in serial.tools.list_ports.comports()]
        self.combo.clear()
        self.combo.addItems(serial_ports)
    




        

        



app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())