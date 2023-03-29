#!/usr/bin/python
# Name: Chris Armour
# License: GPL-3
# Lincense URL: https://www.gnu.org/licenses/gpl-3.0.en.html
#This is a Python application for cyber security tasks. It has a GUI interface and it allows users to perform tasks such as chatting with a chatbot, scanning ports, and performing Nmap scans.




import sys
import os
import random
import subprocess
import string
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QFont, QColor,  QPalette, QPixmap, QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTextEdit, QLineEdit, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QCheckBox, QSizePolicy, QStackedLayout,
                             QSlider, QAbstractItemView, QHeaderView, )
from resources.chatbot import ChatBotApp
from resources.scanner import Scanner

resource_dir = os.path.join(os.path.dirname(__file__), "resources")

class ChatbotWorker(QObject):
    # Define a signal for updating the GUI when the scan is completed
    message_received = pyqtSignal(str)

    def __init__(self, message, chatbot):
        super().__init__()
        self.chatbot_app = chatbot
        self.user_message = message

    def run(self):
        response = self.chatbot_app.get_response(self.user_message)
        self.message_received.emit(response)


class ScannerWorker(QObject):
    # Define a signal for updating the GUI when the scan is completed
    scan_completed = pyqtSignal(list)

    def __init__(self, target, port_range, protocol, limit, speed):
        super().__init__()
        self.target = target
        self.port_range = port_range
        self.protocol = protocol
        self.limit = limit
        self.speed = speed

    def run(self):
        scanner = Scanner(self.target, self.port_range, self.protocol, self.limit, self.speed)
        results = scanner.scan()
        self.scan_completed.emit(results)

class NmapWorker(QObject):
    nmap_completed = pyqtSignal(str)

    def __init__(self, cidr, start_octet, end_octet, output_file):
        super().__init__()
        self.cidr = cidr
        self.start_octet = start_octet
        self.end_octet = end_octet
        self.output_file = output_file

    def run(self):
        command = ["./resources/nmap_auto.sh", "-C", self.cidr, "-S", self.start_octet, "-E", self.end_octet, "-O", self.output_file]
        subprocess.run(command, check=True, text=True)
        with open(self.output_file, "r") as f:
            output = f.read()
        self.nmap_completed.emit(output)













class MainWindow(QWidget):
    def __init__(self, chatbot):
        super().__init__()

        self.chatbot = chatbot

        self.setWindowTitle("Armour Security Toolkit by Chris Armour")
        self.resize(1280, 720)

        # Main layout
        main_layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("./resources/logo.png"))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedHeight(200)
        main_layout.addWidget(logo)



        # Top side navigation
        nav_layout = QHBoxLayout()

        self.chatbot_button = QPushButton("Chatbot")
        self.chatbot_button.setEnabled(False)
        self.chatbot_button.clicked.connect(self.load_chatbot)
       

        self.port_scanner_button = QPushButton("Port Scanner")
        self.port_scanner_button.clicked.connect(self.load_port_scanner)

        self.nmap_button = QPushButton("Nmap")
        self.nmap_button.clicked.connect(self.load_nmap)

        self.password_gen_button = QPushButton("Password Generator")
        self.password_gen_button.clicked.connect(self.load_password_gen)

        nav_layout.addWidget(self.chatbot_button)
        nav_layout.addWidget(self.port_scanner_button)
        nav_layout.addWidget(self.nmap_button)
        nav_layout.addWidget(self.password_gen_button)

 
        nav_layout


        main_layout.addLayout(nav_layout)

        # Stacked layout to switch between programs
        self.stacked_layout = QStackedLayout()
        main_layout.addLayout(self.stacked_layout)

        # Program 1 - Chatbot
        self.chatbot_widget = QWidget()
        self.chatbot_layout = QVBoxLayout(self.chatbot_widget)

        # Chat History
        self.chat_label = QLabel("Chat History")
        self.chat_history = QTextEdit()
        self.chat_history.setFont(QFont("Arial", 15))
        self.chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.chat_history.setReadOnly(True)

        # User Input
        self.input_label = QLabel("Your Message")
        self.chatbot_input_field = QTextEdit()
        self.chatbot_input_field.setFixedHeight(100)
        self.chatbot_input_field.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.send_message_thread)


        # Add widgets to layout
        self.chatbot_layout.addWidget(self.chat_label)
        self.chatbot_layout.addWidget(self.chat_history)
        self.chatbot_layout.addWidget(self.input_label)
        self.chatbot_layout.addWidget(self.chatbot_input_field)
        self.chatbot_layout.addWidget(self.submit_button)

        self.stacked_layout.addWidget(self.chatbot_widget)

        # Program 2 - Port Scanner 


        self.port_scanner_widget = QWidget()
        self.port_scanner_layout = QVBoxLayout(self.port_scanner_widget)

        # Start Scan
        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.clicked.connect(self.start_scan_thread)

        # Target
        self.target_label = QLabel("Target")
        self.target_field = QLineEdit()
        self.target_field.setText("localhost")

        # This Machine checkbox set to localhost

        self.this_machine_checkbox = QCheckBox("This Machine")
        self.this_machine_checkbox.setChecked(False)
        self.this_machine_checkbox.stateChanged.connect(self.this_machine_changed)

        # Port Range default 0-1024
        self.port_range_label = QLabel("Port Range")
        self.port_range_field = QLineEdit()
        self.port_range_field.setText("0-1024")

        # Speed fast slow custom, custom will need an input field
        self.speed_label = QLabel("Speed")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Fast", "Slow", "Custom"])
        self.speed_combo.currentTextChanged.connect(self.speed_changed)

        self.speed_field_label = QLabel("ms")
        self.speed_field = QLineEdit()
        self.speed_field.setText("100")
        self.speed_field.setDisabled(True)

        # Limit scan limit checkbox, if checked will need an input field
        self.scan_limit_label = QLabel("Scan Lmit")
        self.scan_limit_field = QLineEdit()
        self.scan_limit_field.setText("1000")
        self.scan_limit_field_label = QLabel("ms")

        # Protocol
        self.protocol_label = QLabel("Protocol")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP"])

        # Show open ports only checkbox
        self.show_open_ports_checkbox = QCheckBox("Show Open Ports Only")
        self.show_open_ports_checkbox.setChecked(False)
        self.show_open_ports_checkbox.stateChanged.connect(self.filter_table)


        # Scan Results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)

        self.result_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Add this line

        viewport_width = self.result_table.viewport().width()
        scrollbar_width = self.result_table.verticalScrollBar().width() if self.result_table.verticalScrollBar().isVisible() else 0
        table_width = viewport_width - scrollbar_width
        self.result_table.verticalHeader().setVisible(False)

        # Result Table
        self.result_table.setColumnWidth(0, int(table_width * 0.2))  # 20%
        self.result_table.setColumnWidth(1, int(table_width * 0.1))  # 10%
        self.result_table.setColumnWidth(2, int(table_width * 0.1))  # 10%
        self.result_table.setColumnWidth(3, int(table_width * 0.4))  # 30%
        self.result_table.setColumnWidth(4, int(table_width * 0.2))  # 20%
        self.result_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.result_table.setHorizontalHeaderLabels(["Target", "Port", "Status", "Service", "Description"])

        self.result_table.setRowCount(10)
        self.result_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # read only
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Itemclicked trigger
        self.result_table.itemClicked.connect(self.show_scan_details)

        # Scan Detail per result (Port, Service, Description)
        self.scan_detail_table = QTableWidget()
        self.scan_detail_table.horizontalHeader().setVisible(False)
        self.scan_detail_table.verticalHeader().setVisible(False)  
        self.scan_detail_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.scan_detail_table.setRowCount(4)
        self.scan_detail_table.setColumnCount(2)
        self.scan_detail_table.setColumnWidth(0, 100)  

        self.scan_detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # read only
        self.scan_detail_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Set the row labels as QTableWidgetItem objects in the first column
        row_labels = ["Port", "Status",  "Service", "Description"]
        for row in range(self.scan_detail_table.rowCount()):
            item = QTableWidgetItem(row_labels[row])
            self.scan_detail_table.setItem(row, 0, item)

        # Start Scan, Target, This Machine, Port Range
        scan_layout = QHBoxLayout()
        scan_layout.addWidget(self.start_scan_button)
        scan_layout.addWidget(self.target_label)
        scan_layout.addWidget(self.target_field)
        scan_layout.addWidget(self.this_machine_checkbox)
        scan_layout.addWidget(self.port_range_label)
        scan_layout.addWidget(self.port_range_field)
        self.port_scanner_layout.addLayout(scan_layout)

        # Speed, Scan Limit, Protocol, Show Open Ports Only
        scan_options_layout = QHBoxLayout()
        scan_options_layout.addWidget(self.protocol_label)
        scan_options_layout.addWidget(self.protocol_combo)
        scan_options_layout.addWidget(self.speed_label)
        scan_options_layout.addWidget(self.speed_combo)
        scan_options_layout.addWidget(self.speed_field)
        scan_options_layout.addWidget(self.speed_field_label)
        scan_options_layout.addWidget(self.scan_limit_label)
        scan_options_layout.addWidget(self.scan_limit_field)
        scan_options_layout.addWidget(self.scan_limit_field_label)
        scan_options_layout.addWidget(self.show_open_ports_checkbox)
        self.port_scanner_layout.addLayout(scan_options_layout)

        # Scan Results
        self.port_scanner_layout.addWidget(self.result_table)
  
        # Scan Detail
        self.port_scanner_layout.addWidget(self.scan_detail_table)

        # Add to stacked layout
        self.stacked_layout.addWidget(self.port_scanner_widget)

        # Program 3 - Nmap gui
        self.nmap_widget = QWidget()
        self.nmap_layout = QVBoxLayout(self.nmap_widget)

        # Run Nmap
        self.run_nmap_button = QPushButton("Run Nmap")
        self.run_nmap_button.clicked.connect(self.run_nmap_thread)

        # Cidr
        self.cidr_label = QLabel("CIDR:")
        self.cidr_field = QLineEdit()
        self.cidr_field.setText("192.168.0")
    
        # Start Octet
        self.start_octet_label = QLabel("Start Octet:")
        self.start_octet_field = QLineEdit()
        self.start_octet_field.setText("1")

        # End Octet
        self.end_octet_label = QLabel("End Octet:")
        self.end_octet_field = QLineEdit()
        self.end_octet_field.setText("255")

        # Output File name
        self.output_file_label = QLabel("Output File Name:")
        self.output_file_field = QLineEdit()
        self.output_file_field.setText("nmap_output.txt")

        # Nmap Options Layout
        nmap_options_layout = QHBoxLayout()
        nmap_options_layout.addWidget(self.run_nmap_button)
        
        nmap_options_layout.addWidget(self.cidr_label)
        nmap_options_layout.addWidget(self.cidr_field)
        nmap_options_layout.addWidget(self.start_octet_label)
        nmap_options_layout.addWidget(self.start_octet_field)
        nmap_options_layout.addWidget(self.end_octet_label)
        nmap_options_layout.addWidget(self.end_octet_field)
        nmap_options_layout.addWidget(self.output_file_label)
        nmap_options_layout.addWidget(self.output_file_field)
        self.nmap_layout.addLayout(nmap_options_layout)

        #Nmap Output
        self.nmap_output = QTextEdit()
        self.nmap_output.setReadOnly(True)
        self.nmap_layout.addWidget(self.nmap_output)


        # Add to stacked layout
        self.stacked_layout.addWidget(self.nmap_widget)


        # Program 4 - Password Generator
        self.password_generator_widget = QWidget()
        self.password_generator_layout = QVBoxLayout(self.password_generator_widget)

        # Generator Lable
        self.generator_label = QLabel("Password Generator")
        self.generator_label.setFont(QFont("Courier New", 50, QFont.Weight.Bold))
        self.password_generator_layout.addWidget(self.generator_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Generate Password Button
        self.generate_password_button = QPushButton("Generate")
        self.generate_password_button.clicked.connect(self.generate_password)
        self.generate_password_button.setFixedWidth(100)

        # Copy Password Button
        self.copy_password_button = QPushButton("Copy")
        self.copy_password_button.clicked.connect(self.copy_password)
        self.copy_password_button.setFixedWidth(100)





        # Generated Password
        self.generated_password = QLineEdit()
        self.generated_password.setFixedWidth(1000)
        self.generated_password.setFont(QFont("Arial", 25))
        self.generated_password.setAlignment(Qt.AlignmentFlag.AlignCenter)

        

        # Password Length
        
        self.password_length_slider = QSlider(Qt.Orientation.Horizontal)
        self.password_length_slider.setMinimum(4)
        self.password_length_slider.setMaximum(40)
        self.password_length_slider.setValue(10)
        self.password_length_slider.setTickInterval(1)
        self.password_length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.password_length_slider.valueChanged.connect(self.generate_password)
        self.password_length_label = QLabel("Password Length:" + str(self.password_length_slider.value()))

        


        # Password Settings

        # Letters
        self.letters_checkbox = QCheckBox("Letters (e.g. Aa - Zz)")
        self.letters_checkbox.setChecked(True)
        self.letters_checkbox.stateChanged.connect(self.generate_password)


        # Digits
        self.digits_checkbox = QCheckBox("Digits (e.g. 0 - 9))")
        self.digits_checkbox.setChecked(True)
        self.digits_checkbox.stateChanged.connect(self.generate_password)

        # Symbols
        self.symbols_checkbox = QCheckBox("Symbols (e.g. !@#$%^&*()")
        self.symbols_checkbox.setChecked(True)
        self.symbols_checkbox.stateChanged.connect(self.generate_password)


        self.password_generator_layout.addWidget(self.generated_password, alignment=Qt.AlignmentFlag.AlignCenter)

        # Password Settings Layout
        password_settings_layout = QVBoxLayout()
        password_settings_layout.addWidget(self.letters_checkbox)
        password_settings_layout.addWidget(self.digits_checkbox)
        password_settings_layout.addWidget(self.symbols_checkbox)






       

        self.password_generator_layout.addLayout(password_settings_layout)

        # Password Length Layout
        password_length_layout = QHBoxLayout()
        password_length_layout.addWidget(self.password_length_label)
        password_length_layout.addWidget(self.password_length_slider)
    
        self.password_generator_layout.addLayout(password_length_layout)

        # Generated Password Layout
        generated_password_layout = QHBoxLayout()
        
        generated_password_layout.addWidget(self.generate_password_button, alignment=Qt.AlignmentFlag.AlignCenter)
        generated_password_layout.addWidget(self.copy_password_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.password_generator_layout.addLayout(generated_password_layout)

        # Add to stacked layout
        self.stacked_layout.addWidget(self.password_generator_widget)

        self.setLayout(main_layout)

    # Load Chatbot
    def load_chatbot(self):
        self.port_scanner_button.setEnabled(True)
        self.nmap_button.setEnabled(True)
        self.chatbot_button.setEnabled(False)
        self.stacked_layout.setCurrentWidget(self.chatbot_widget)

    # Load Port Scanner
    def load_port_scanner(self):
        self.port_scanner_button.setEnabled(False)
        self.nmap_button.setEnabled(True)
        self.chatbot_button.setEnabled(True)
        self.stacked_layout.setCurrentWidget(self.port_scanner_widget)

        # Show all rows when the view is loaded
        for row in range(self.result_table.rowCount()):
            self.result_table.showRow(row)

    # Load Nmap
    def load_nmap(self):
        self.port_scanner_button.setEnabled(True)
        self.nmap_button.setEnabled(False)
        self.chatbot_button.setEnabled(True)
        self.stacked_layout.setCurrentWidget(self.nmap_widget)

    # Load Password Generator
    def load_password_gen(self):
        self.port_scanner_button.setEnabled(True)
        self.nmap_button.setEnabled(True)
        self.chatbot_button.setEnabled(True)
        self.stacked_layout.setCurrentWidget(self.password_generator_widget)


    # Target field disabled if this machine is checked
    def this_machine_changed(self):
        if self.this_machine_checkbox.isChecked():
            self.target_field.setText("localhost")
            self.target_field.setDisabled(True)
        else:
            self.target_field.setText("")
            self.target_field.setDisabled(False)


    # Custom Speed enabled/disabled
    def speed_changed(self):
        if self.speed_combo.currentText() == "Custom":
            self.speed_field.setDisabled(False)
        else:
            self.speed_field.setDisabled(True)

    # Send message to chatbot
    def send_message_thread(self):
        message = self.chatbot_input_field.toPlainText()
        self.chatbot_input_field.clear()
        
        self.chat_history.append( message + ": User") 
        self.chat_history.setAlignment(Qt.AlignmentFlag.AlignRight)
        


        self.chatbot_worker = ChatbotWorker(message, self.chatbot)
        self.chatbot_thread = QThread()
        self.chatbot_worker.moveToThread(self.chatbot_thread)

        self.chatbot_thread.started.connect(self.chatbot_worker.run)
        self.chatbot_worker.message_received.connect(self.update_chatbot)
        self.chatbot_worker.message_received.connect(self.chatbot_thread.quit)
        self.chatbot_worker.message_received.connect(self.chatbot_worker.deleteLater)
        self.chatbot_thread.finished.connect(self.chatbot_thread.deleteLater)

        self.chatbot_thread.start()

    # Update chatbot
    def update_chatbot(self, message):
        
        self.chat_history.append("Bot: " + message)
        self.chat_history.setAlignment(Qt.AlignmentFlag.AlignLeft)
        

    
    # Start Scan

    def start_scan_thread(self):
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.setText("Scanning...")
        target = self.target_field.text()
        port_range = self.port_range_field.text()
        protocol = self.protocol_combo.currentText()
        limit = self.scan_limit_field.text()
        speed = 1000 if self.speed_combo.currentText() == "Fast" else 3000 if self.speed_combo.currentText() == "Slow" else float(self.speed_field.text())

        self.scanner_worker = ScannerWorker(target, port_range, protocol, limit, speed)
        self.scanner_thread = QThread()
        self.scanner_worker.moveToThread(self.scanner_thread)

        self.scanner_thread.started.connect(self.scanner_worker.run)
        self.scanner_worker.scan_completed.connect(self.update_results)
        self.scanner_worker.scan_completed.connect(self.enable_start_scan_button)
        self.scanner_worker.scan_completed.connect(self.scanner_thread.quit)
        self.scanner_worker.scan_completed.connect(self.scanner_worker.deleteLater)
        self.scanner_thread.finished.connect(self.scanner_thread.deleteLater)

        self.scanner_thread.start()
    
    # Enable start scan button
    def enable_start_scan_button(self):
        self.start_scan_button.setEnabled(True)
        self.start_scan_button.setText("Start Scan")
    
    # Update results table
    def update_results(self, results):
        self.result_table.setRowCount(len(results))

        for i, result in enumerate(results):
            target_item = QTableWidgetItem(result["target"])
            port_item = QTableWidgetItem(str(result["port"]))
            status_item = QTableWidgetItem(result["status"])
            service_item = QTableWidgetItem(result["service"])
            description_item = QTableWidgetItem(result["description"])

            self.result_table.setItem(i, 0, target_item)
            self.result_table.setItem(i, 1, port_item)
            self.result_table.setItem(i, 2, status_item)
            self.result_table.setItem(i, 3, service_item)
            self.result_table.setItem(i, 4, description_item)
    
    # Filter open ports only if checkbox is checked
    def filter_table(self):
        if self.show_open_ports_checkbox.isChecked():
            for row in range(self.result_table.rowCount()):
                if self.result_table.item(row, 2).text() == "Open":
                    self.result_table.showRow(row)
                else:
                    self.result_table.hideRow(row)
        else:
            for row in range(self.result_table.rowCount()):
                self.result_table.showRow(row)

    # Show scan details when a row is clicked
    def show_scan_details(self, item: QTableWidgetItem):
        selected_row = item.row()

        port_item = self.result_table.item(selected_row, 1)
        status_item = self.result_table.item(selected_row, 2)
        service_item = self.result_table.item(selected_row, 3)
        description_item = self.result_table.item(selected_row, 4)

        port_detail_item = QTableWidgetItem(port_item.text())
        status_detail_item = QTableWidgetItem(status_item.text())
        service_detail_item = QTableWidgetItem(service_item.text())
        description_detail_item = QTableWidgetItem(description_item.text())

        self.scan_detail_table.setItem(0, 1, port_detail_item)
        self.scan_detail_table.setItem(1, 1, status_detail_item)
        self.scan_detail_table.setItem(2, 1, service_detail_item)
        self.scan_detail_table.setItem(3, 1, description_detail_item)
    
    # Start Nmap Scan
    def run_nmap_thread(self):
        cidr = self.cidr_field.text()
        start_octet = self.start_octet_field.text()
        end_octet = self.end_octet_field.text()
        output_file = self.output_file_field.text()

        self.nmap_worker = NmapWorker(cidr, start_octet, end_octet, output_file)
        self.nmap_thread = QThread()
        self.nmap_worker.moveToThread(self.nmap_thread)

        self.nmap_thread.started.connect(self.nmap_worker.run)
        self.nmap_worker.nmap_completed.connect(self.update_nmap_output)
        self.nmap_worker.nmap_completed.connect(self.nmap_thread.quit)
        self.nmap_worker.nmap_completed.connect(self.nmap_worker.deleteLater)
        self.nmap_thread.finished.connect(self.nmap_thread.deleteLater)

        self.nmap_thread.start()
    
    # Update Nmap output
    def update_nmap_output(self, output):
        self.nmap_output.setPlainText(output)

    # Password Generator Thread
    def generate_password(self):
        length = self.password_length_slider.value()
        include_letters = self.letters_checkbox.isChecked()
        include_numbers = self.digits_checkbox.isChecked()
        include_symbols = self.symbols_checkbox.isChecked()
        
        # Update password length label
        self.password_length_label.setText(f"Length: {length}")

        # Letters Available
        letters = string.ascii_letters
        # Numbers Available
        numbers = string.digits
        # Symbols Available
        symbols = string.punctuation

        # Create a list of all available characters
        available_characters = []
        if include_letters:
            available_characters.extend(letters)
        if include_numbers:
            available_characters.extend(numbers)
        if include_symbols:
            available_characters.extend(symbols)

        # Random Seed
       

        # Generate password
        password = ""
        for i in range(int(length)):
            random.seed()
            password += random.choice(available_characters)

        self.generated_password.setText(password)

    # Copy password to clipboard
    def copy_password(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_password.text())
        # Show copied message for 1 second
        self.copy_password_button.setText("Copied!")
        QTimer.singleShot(1000, lambda: self.copy_password_button.setText("Copy"))


def main():
    app = QApplication(sys.argv)

    app_icon = QIcon("/resources/icon.png")
    app.setWindowIcon(app_icon)

    app.setStyle("fusion")
    # Set the color palette to a dark theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase,  QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    chatbot = ChatBotApp()
    window = MainWindow(chatbot)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
