# -*- coding: utf-8 -*-
"""
Estilos CSS para formularios de inspección
Extraído del inspection_form_dialog.py para mejor organización
"""

# Estilo principal del dialog de inspección
INSPECTION_DIALOG_STYLE = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f8f9fa, stop:1 #e9ecef);
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: white;
    padding: 10px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB74D, stop:1 #FFA726);
    border-radius: 8px;
    margin-bottom: 15px;
}

QLabel {
    font-weight: bold;
    color: #2c3e50;
    font-size: 11px;
    min-width: 120px;
}

QLineEdit, QComboBox, QTextEdit {
    padding: 8px;
    border: 2px solid #ced4da;
    border-radius: 4px;
    background: white;
    color: black;
    font-size: 11px;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    width: 10px;
    height: 10px;
}

QComboBox QAbstractItemView {
    background: white;
    color: black;
    border: 1px solid #FFA726;
    selection-background-color: #FFE0B2;
    selection-color: black;
}

QComboBox::item {
    background: white;
    color: black;
    padding: 5px;
}

QComboBox::item:selected {
    background: #FFE0B2;
    color: black;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 2px solid #FFA726;
    background: #fff8f0;
    color: black;
}

QPushButton#saveButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB74D, stop:1 #FFA726);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
    min-width: 120px;
}

QPushButton#saveButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFA726, stop:1 #FF9800);
}

QPushButton#cancelButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6c757d, stop:1 #545b62);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
    min-width: 120px;
}

QPushButton#cancelButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #545b62, stop:1 #4a4f55);
}

QScrollArea#scrollArea {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB74D, stop:1 #FFA726);
    border: none;
}

QWidget#scrollWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB74D, stop:1 #FFA726);
}

QFrame#formFrame {
    background: white;
    border-radius: 8px;
    padding: 15px;
    border: none;
}
"""

# Estilo para mensajes de advertencia
WARNING_MESSAGE_STYLE = """
QMessageBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f8f9fa, stop:1 #fff3e0);
    border-radius: 8px;
    min-width: 360px;
    max-height: 120px;
    min-height: 100px;
}

QMessageBox QLabel {
    font-size: 13px;
    color: #2c3e50;
    padding: 8px;
    font-family: Arial, sans-serif;
    background: transparent;
    min-width: 340px;
    text-align: left;
}

QMessageBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB74D, stop:1 #FFA726);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 20px;
    font-size: 12px;
    font-weight: bold;
    font-family: Arial, sans-serif;
    min-width: 70px;
}

QMessageBox QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFA726, stop:1 #FF9800);
}

QMessageBox QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FF9800, stop:1 #F57C00);
}
"""

# Estilo para mensajes de éxito
SUCCESS_MESSAGE_STYLE = """
QMessageBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f0f8f0, stop:1 #e8f5e8);
    border-radius: 8px;
    min-width: 380px;
    min-height: 140px;
}

QMessageBox QLabel {
    font-size: 13px;
    color: #2c3e50;
    padding: 10px;
    font-family: Arial, sans-serif;
    background: transparent;
    min-width: 340px;
}

QMessageBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #66BB6A, stop:1 #4CAF50);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 25px;
    font-size: 13px;
    font-weight: bold;
    font-family: Arial, sans-serif;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4CAF50, stop:1 #388E3C);
}

QMessageBox QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #388E3C, stop:1 #2E7D32);
}
""" 