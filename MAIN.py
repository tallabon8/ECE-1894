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
        self.waterResetTimes = []
        self.foodResetTimes = []
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
        self.pushButton_3.clicked.connect(self.on_pushButton_3_clicked) #i need to implement this portion
        #check for refill food
        self.pushButton_2.clicked.connect(self.on_pushButton_2_clicked) #i need to implement this portion
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
        self.recordValueTimer.start(3600000) 
        self.waterRecordTimer = QTimer(self)
        self.waterRecordTimer.timeout.connect(self.recordWaterAverage)
        self.waterRecordTimer.start(10000)

        self.foodRecordTimer = QTimer(self)
        self.foodRecordTimer.timeout.connect(self.recordFoodAverage)
        self.foodRecordTimer.start(10000)
        
        self.lcdNumber.display(25) #default value for 
        self.lcdNumber_5.display(72.8) #default value for humidity
        self.lcdNumber_3.display(0) #default value for water purity

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

    def on_pushButton_3_clicked(self):
        self.waterResetTimes.append(self.elapsedSeconds)
        self.elapsedSeconds = 0
        self.sys_time_label.setText("00:00:00")
        self.calculateAverage()

    def on_pushButton_2_clicked(self):
        self.foodResetTimes.append(self.elapsedSeconds_2)
        self.elapsedSeconds_2 = 0
        self.sys_time_label_2.setText("00:00:00")
        self.calculateAverage()
    
    def calculateAverage(self):
        if not self.waterResetTimes:
            self.sys_time_label_3.setText("00:00:00")
            return
        totalWaterTime = sum(self.waterResetTimes)
        averageWaterTime = totalWaterTime / len(self.waterResetTimes)
        self.sys_time_label_3.setText(str(QTime(0, 0, 0).addSecs(int(averageWaterTime)).toString("hh:mm:ss")))
        if not self.foodResetTimes:
            self.sys_time_label_3.setText("00:00:00")
            return
        totalFoodTime = sum(self.foodResetTimes)
        averageFoodTime = totalFoodTime / len(self.foodResetTimes)
        self.sys_time_label_4.setText(str(QTime(0, 0, 0).addSecs(int(averageFoodTime)).toString("hh:mm:ss")))

    def recordWaterAverage(self):
        self.waterResetTimes = []
        self.waterResetTimes.append(self.elapsedSeconds)
        self.elapsedSeconds = 0
        average_water_time = sum(self.waterResetTimes) / len(self.waterResetTimes)
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.saveWaterAverageToCsv(current_time, average_water_time)

    def recordFoodAverage(self):
        self.foodResetTimes = []
        self.foodResetTimes.append(self.elapsedSeconds_2)
        self.elapsedSeconds_2 = 0
        average_food_time = sum(self.foodResetTimes) / len(self.foodResetTimes)
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.saveFoodAverageToCsv(current_time, average_food_time)

    def saveWaterAverageToCsv(self, timestamp, value):
        file_name = "water_average.csv"
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, value])

    def saveFoodAverageToCsv(self, timestamp, value):
        file_name = "food_average.csv"
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, value])

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