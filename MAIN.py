#test
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QTimer, QDateTime, QTime
import csv
import sys

# Import the Ui_MainWindow class from your generated file
from MamaSarahUI_with_mqtt import Ui_MainWindow
from clickable_label import ClickableLabel

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        #deals with initializing to 00:00:00, for time since water refill
        self.timerResetCountWater = []
        self.timerResetCountFood = []
        #push_Button_3 is the refill water button
        self.sys_time_label.setText("00:00:00") #time since water fill
        self.sys_time_label_3.setText("00:00:00") #24hr average time since water fill
        self.elapsedSeconds = 0
        self.sysTimeUpdateTimer = QTimer(self)
        self.sysTimeUpdateTimer.timeout.connect(self.incrementSysTimeLabel)
        self.sysTimeUpdateTimer.start(1000)
        #deals with initializing to 00:00:00, for time since food refill
        #push_Button_2 is the refill food button
        self.sys_time_label_2.setText("00:00:00") #time since food fill
        self.sys_time_label_4.setText("00:00:00") #24hr average time since food fill
        self.elapsedSeconds_2 = 0
        self.sysTimeUpdateTimer = QTimer(self)
        self.sysTimeUpdateTimer.timeout.connect(self.incrementSysTimeLabel_2)
        self.sysTimeUpdateTimer.start(1000)
        #check for refill water
        self.pushButton_3.clicked.connect(self.calculateDisplayAvgWater)
        #check for refill food
        self.pushButton_2.clicked.connect(self.calculateDisplayAvgFood)
        #updating Zigbee Devices
        self.pushButton_5.clicked.connect(self.addItemToListView)
        self.model = QStandardItemModel(self.listView)
        self.listView.setModel(self.model)
        #Updating Egg Count
        self.pushButton_4.clicked.connect(self.incrementLcdNumber2)
        #Reset Egg Count
        self.pushButton.clicked.connect(self.resetLcdNumber2)
        self.ebrake_fail_on = self.convertToClickableLabel(self.ebrake_fail_on)
        self.ebrake_fail_off = self.convertToClickableLabel(self.ebrake_fail_off)
        # Connect the clickable labels to functions
        self.ebrake_fail_on.clicked.connect(self.lightsOn)
        self.ebrake_fail_off.clicked.connect(self.lightsOff)

        self.recordValueTimer = QTimer(self)
        self.recordValueTimer.timeout.connect(self.recordLcdNumber2Value)
        self.recordValueTimer.start(10000) 

    def incrementSysTimeLabel(self):
        # Increment the elapsed time by 1 second
        self.elapsedSeconds += 1
        # Calculate the new time to display
        timeToDisplay = QTime(0, 0, 0).addSecs(self.elapsedSeconds)
        # Update the sys_time_label with the new time
        self.sys_time_label.setText(timeToDisplay.toString("hh:mm:ss"))

    def incrementSysTimeLabel_2(self):
        self.elapsedSeconds_2 += 1
        # Calculate the new time to display
        timeToDisplay = QTime(0, 0, 0).addSecs(self.elapsedSeconds_2)
        # Update the sys_time_label with the new time
        self.sys_time_label_2.setText(timeToDisplay.toString("hh:mm:ss"))
    def calculateAverageTime(self):
        totalSeconds = 0
        for time in self.timerResetCountWater:
            secondsSinceMidnight = QTime(0, 0, 0).secsTo(time.time())
            totalSeconds += secondsSinceMidnight
        averageSeconds = totalSeconds / len(self.timerResetCountWater)
        averageTime = QTime(0, 0, 0).addSecs(int(averageSeconds))
        return averageTime

    def startRefillWater(self):
        self.sys_time_label_3.setText("00:00:00")

    def calculateDisplayAvgWater(self):
        if not self.timerResetCountWater:
            self.sys_time_label_3.setText("00:00:00")
            return QTime(0, 0, 0)  # Return default QTime if list is empty
        
        totalSeconds = 0
        for time in self.timerResetCountWater:
            secondsSinceMidnight = QTime(0, 0, 0).secsTo(time.time())
            totalSeconds += secondsSinceMidnight
        
        averageSeconds = totalSeconds / len(self.timerResetCountWater)
        averageTime = QTime(0, 0, 0).addSecs(int(averageSeconds))
        self.sys_time_label_3.setText(averageTime.toString("hh:mm:ss"))
        return averageTime  # Return the calculated average time

    def calculateDisplayAvgFood(self):
        if not self.timerResetCountFood:
            self.sys_time_label_4.setText("00:00:00")
            return QTime(0, 0, 0)  # Return default QTime if list is empty
        
        totalSeconds = 0
        for time in self.timerResetCountFood:
            secondsSinceMidnight = QTime(0, 0, 0).secsTo(time.time())
            totalSeconds += secondsSinceMidnight
        
        averageSeconds = totalSeconds / len(self.timerResetCountFood)
        averageTime = QTime(0, 0, 0).addSecs(int(averageSeconds))
        self.sys_time_label_4.setText(averageTime.toString("hh:mm:ss"))
        return averageTime  # Return the calculated average time

    def startRefillFood(self):
        self.sys_time_label_4.setText("00:00:00")
        
    def msecs(self, time):
        return ((time.hour() * 3600) + (time.minute() * 60) + time.second()) * 1000 + time.msec()

    def updateRefillDuration(self):
        # Calculate the duration since the last refill start
        duration = self.lastRefillStartTime.secsTo(QDateTime.currentDateTime())
        self.sys_time_label.setText(QTime(0, 0, 0).addSecs(duration).toString("hh:mm:ss"))
        
        # When button pressed again, update the average duration
        self.refillDurations.append(duration)
        #self.refillTimer.stop()  # Stop the timer until the next refill start
        # Set default values for LCDs
        self.lcdNumber.display(25)
        self.lcdNumber_5.display(72.8)
        self.lcdNumber_3.display(0)

        # Flags to determine if sys_time_labels should be updated
        self.updateSysTimeLabel = True
        self.updateSysTimeLabel2 = True

        # Connect button clicks to their respective functions
        self.pushButton.clicked.connect(self.resetLcdNumber2)
        self.pushButton_2.clicked.connect(self.calculateDisplayAvgFood)
        self.pushButton_3.clicked.connect(self.calculateDisplayAvgWater)
        self.pushButton_4.clicked.connect(self.incrementLcdNumber2)
        
        self.ebrake_fail_off = self.convertToClickableLabel(self.ebrake_fail_off)
        self.ebrake_fail_on = self.convertToClickableLabel(self.ebrake_fail_on)

 
        
        # Timer for updating sys_time_labels with time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # milliseconds

        # Initialize the model for listView and populate it
        self.initializeListView()

    def convertToClickableLabel(self, label):
        clickable_label = ClickableLabel(label.parent())
        clickable_label.setGeometry(label.geometry())
        clickable_label.setText(label.text())
        clickable_label.setStyleSheet(label.styleSheet())
        label.deleteLater()
        return clickable_label

    def incrementLcdNumber2(self):
        current_value = self.lcdNumber_2.value()
        self.lcdNumber_2.display(current_value + 1)
    
    def resetLcdNumber2(self):
        self.lcdNumber_2.display(0)

    def recordLcdNumber2Value(self):
            current_value = self.lcdNumber_2.value()
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            self.saveLcdNumber2ValueToCsv(current_time, current_value)

    def saveLcdNumber2ValueToCsv(self, timestamp, value):
        file_name = "egg_count.csv"
        # Open the file in append mode, create if does not exist
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            # Write the data
            writer.writerow([timestamp, value])
        
    def toggleSysTimeLabelUpdate(self, shouldUpdate):
        self.updateSysTimeLabel = shouldUpdate
        if not shouldUpdate:
            self.sys_time_label.setText("00:00:00")
    
    def toggleSysTimeLabel2Update(self, shouldUpdate):
        self.updateSysTimeLabel2 = shouldUpdate
        if not shouldUpdate:
            self.sys_time_label_2.setText(QDateTime.currentDateTime().toString("hh:mm:ss"))

    def lightsOff(self):
        print("Lights off")
    
    def lightsOn(self):
        print("Lights on")

    def addItemToListView(self):
        serialNoContent = self.textEdit.toPlainText().strip()
        deviceNameContent = self.textEdit_2.toPlainText().strip()
        if serialNoContent and deviceNameContent:
            # Get text from textEdit and textEdit_2
            textEditContent = self.textEdit.toPlainText()
            textEdit2Content = self.textEdit_2.toPlainText()
            # Combine the text from both textEdits, you can format it as you like
            combinedText = f"Serial No: {textEditContent},  Device Name: {textEdit2Content}"
            # Create a new item with combined text
            newItem = QStandardItem(combinedText)
            # Add the new item to the model
            self.model.appendRow(newItem)
            self.textEdit.clear()
            self.textEdit_2.clear()
        else:
            print("Please enter a serial number and device name")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())