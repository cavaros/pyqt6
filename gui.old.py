import sys
import subprocess
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit

class SystemdServiceLister(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Systemd Service Lister')

        self.button = QPushButton('List Services', self)
        self.button.clicked.connect(self.list_services)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.textbox)

    def list_services(self):
        result = subprocess.run(['systemctl', '--user', '--all', 'list-units', '--type=service'], capture_output=True, text=True)
        self.textbox.setText(result.stdout)

def main():
    app = QApplication(sys.argv)

    window = SystemdServiceLister()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
