import os
import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QPushButton,
)
from PySide6.QtCore import Qt, QSettings


class SystemdServiceLister(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings(os.getenv("USER"), "systemd-gui")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("User Systemd GUI by ChatGPT")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Service", "Loaded", "Active", "Sub", "Toggle"]
        )
        # Change the section resize mode to Interactive so the user can resize the columns
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.list_services()

        # Set the size of the window to 500x500 pixels
        self.resize(650, 500)

        # Restore column widths
        for i in range(self.table.columnCount()):
            width = self.settings.value(
                f"column_{i}_width", 100, type=int
            )  # Default width is 100
            self.table.setColumnWidth(i, width)

    def closeEvent(self, event):
        # Save column widths
        for i in range(self.table.columnCount()):
            self.settings.setValue(f"column_{i}_width", self.table.columnWidth(i))

        event.accept()

    def list_services(self):
        result = subprocess.run(
            ["systemctl", "--user", "--all", "list-units", "--type=service"],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.splitlines()

        # Ignore the summary lines at the end
        lines = [
            line
            for line in lines
            if line
            and not any(map(line.__contains__, ["JOB", "LOAD", "ACTIVE", "SUB"]))
            and not "loaded units listed" in line
            and not "To show all installed unit files" in line
        ]

        self.table.setRowCount(len(lines))

        for i, line in enumerate(lines):
            words = line.split()
            if len(words) > 0:
                if words[0].startswith("●"):
                    words.pop(0)
                service = words[0]
                loaded = words[1]
                active = words[2]
                sub = words[3]
                self.table.setItem(i, 0, QTableWidgetItem(service))
                self.table.setItem(i, 1, QTableWidgetItem(loaded))
                self.table.setItem(i, 2, QTableWidgetItem(active))
                self.table.setItem(i, 3, QTableWidgetItem(sub))

                # Determine the action based on the service status
                action = "stop" if sub == "running" else "start"
                button = QPushButton(action.capitalize())
                button.clicked.connect(self.create_service_action(service, action, i))
                # Color button red if stop and green if start
                if action == "stop":
                    button.setStyleSheet("background-color: #8b0000;")
                else:
                    button.setStyleSheet("background-color: green;")

                self.table.setCellWidget(i, 4, button)

    def create_service_action(self, service, action, row):
        def service_action():
            result = subprocess.run(
                ["systemctl", "--user", action, service], capture_output=True, text=True
            )
            if result.returncode == 0:
                QMessageBox.information(
                    self,
                    f"{action.capitalize()} Service",
                    f"Successfully {action}ed {service}",
                )
                self.update_service_status(service, row)
            else:
                QMessageBox.critical(
                    self,
                    f"{action.capitalize()} Service",
                    f"Failed to {action} {service}\n\n{result.stderr}",
                )

        return service_action

    def update_service_status(self, service, row):
        result = subprocess.run(
            [
                "systemctl",
                "--user",
                "show",
                "--property=LoadState,ActiveState,SubState",
                service,
            ],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.splitlines()
        loaded = lines[0].split("=")[1]
        active = lines[1].split("=")[1]
        sub = lines[2].split("=")[1]
        self.table.setItem(row, 1, QTableWidgetItem(loaded))
        self.table.setItem(row, 2, QTableWidgetItem(active))
        self.table.setItem(row, 3, QTableWidgetItem(sub))

        # Update the enabled status of the button
        button = self.table.cellWidget(row, 4)
        action = "stop" if sub == "running" else "start"
        if action == "stop":
            button.setStyleSheet("background-color: #8b0000;")
        else:
            button.setStyleSheet("background-color: green;")
        button.setText(action.capitalize())
        button.clicked.disconnect()
        button.clicked.connect(self.create_service_action(service, action, row))


def main():
    app = QApplication(sys.argv)

    window = SystemdServiceLister()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
