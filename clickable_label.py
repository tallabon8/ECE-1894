# clickable_label.py

from PyQt5 import QtWidgets, QtCore

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()  # Define a signal called 'clicked'

    def mousePressEvent(self, event):
        super().mousePressEvent(event)  # Call the parent class' mousePressEvent method
        self.clicked.emit()  # Emit the clicked signal
