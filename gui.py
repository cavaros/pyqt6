import sys
import subprocess
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class SystemdServiceLister(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Systemd Service Lister')

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Service', 'Start', 'Stop', 'Restart'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Set table padding and margin
        self.table.setContentsMargins(10, 10, 10, 10)
        self.table.setStyleSheet("padding:10px;")

        # Set table colors
        palette = self.table.palette()
        palette.setColor(QPalette.Base, QColor(255, 255, 255))  # Background color
        palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Text color
        self.table.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.list_services()

    def list_services(self):
        result = subprocess.run(['systemctl', '--user', 'list-units', '--type=service'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        self.table.setRowCount(len(lines))

        for i, line in enumerate(lines):
            words = line.split()
            if len(words) > 0:
                service = words[0]
                self.table.setItem(i, 0, QTableWidgetItem(service))

                for j, action in enumerate(['start', 'stop', 'restart'], start=1):
                    button = QPushButton(action.capitalize())
                    button.clicked.connect(self.create_service_action(service, action))
                    self.table.setCellWidget(i, j, button)

    def create_service_action(self, service, action):
        def service_action():
            result = subprocess.run(['systemctl', '--user', action, service], capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(self, f'{action.capitalize()} Service', f'Successfully {action}ed {service}')
            else:
                QMessageBox.critical(self, f'{action.capitalize()} Service', f'Failed to {action} {service}\n\n{result.stderr}')

        return service_action

def main():
    app = QApplication(sys.argv)

    window = SystemdServiceLister()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
