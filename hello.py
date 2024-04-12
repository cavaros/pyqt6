import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv) # app = QApplication([])
label = QLabel("<font color=red size=40>Hello World!</font>") # This HTML approach will be valid too!
label.show()
app.exec()