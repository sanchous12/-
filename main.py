import os
import sqlite3
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtSql import *
from PyQt6 import QtWidgets, QtCore, uic
from db import *
import re

Form, Window = uic.loadUiType('main_form.ui')
db_name = 'databases//database.db'

def get_selected_cell():
    table = QTableWidget()
    selection = table.selectionModel()
    indexes = selection.selectedIndexes()
    if indexes:
        index = indexes[0]
        row = index.row()
        column = index.column()
        return table, row, column
    else:
        return None, None, None


def input_cod_grnti():
    """ВВод кода ГРНТИ без разделителей в определенную существующую ячейку"""
    table, row, column = get_selected_cell()
    item = table.item(row, column)
    grnti_pattern = r'\d{2}\.\d{2}\.\d{2}'
    if re.search(grnti_pattern, str(item.text())):
        menu = QMenu()
        clear_action = menu.addAction("Очистить ячейку")
        add_new_code_action = menu.addAction("Добавить новый код")
        action = menu.exec_(table.mapToGlobal(table.visualItemRect(item).center()))

        if action == clear_action:
            table.setItem(row, column, QTableWidgetItem(""))
        elif action == add_new_code_action:
            input_dialog = QInputDialog()
            while True:
                cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ без разделителей и пробелов')
                if not ok or cod is None or cod.isalpha():
                    msg_box = QMessageBox()
                    msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
                    msg_box.exec()
                    return None
                else:
                    break

            cod = add_delimiters_in_cod_grnti(cod)
            result = str(item.text()) + str(cod)
            result.strip()
            table.setItem(row, column, QTableWidgetItem(result))
    else:
        input_dialog = QInputDialog()
        while True:
            cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ без разделителей и пробелов')
            if not ok or cod is None or cod.isalpha():
                msg_box = QMessageBox()
                msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
                msg_box.exec()
                return None
            else:
                break
        cod = add_delimiters_in_cod_grnti(cod)
        result = str(item.text()) + str(cod)
        result.strip()
        table.setItem(row, column, QTableWidgetItem(result))

def add_delimiters_in_cod_grnti(string):
    """Добавление точек между каждой парой цифр в вводимый код ГРНТИ"""
    string = string.strip()
    if len(string) > 8:
        string = string[:9]
    for i in range(2, len(string) - 2, 2):
        string[i] = string[i] + '.'
    return string

def filter_by_cod_grnti():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    input_dialog = QInputDialog()
    while True:
        str_cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ или его часть без разделителей и пробелов')
        if not ok or str_cod is None or str_cod.isalpha():
            msg_box = QMessageBox()
            msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
            msg_box.exec()
            return None
        else:
            break

    str_cod = add_delimiters_in_cod_grnti(str_cod)
    c.execute('''SELECT *   
                            FROM Tp_nir
                            WHERE "Коды_ГРНТИ" LIKE ?''', ('%' + str_cod + '%',))
    rows = c.fetchall()
    headers = [description[0] for description in c.description]
    model = QSqlQueryModel()
    model.setQuery("SELECT * FROM Tp_nir WHERE `Коды_ГРНТИ` LIKE '%" + str_cod + "%'")
    form.tableView.setModel(model)
    form.tableView.show()
    conn.commit()
    conn.close()

name_list=column()
code_list=codes()
#prepare_tables()
#[str(i) + ' ' + var for var, i in zip(name_list, range(1,100))]

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

def connect_db(db_name_name):
    db_name = QSqlDatabase.addDatabase('QSQLITE')
    db_name.setDatabaseName(db_name_name)
    if not db_name.open():
        print('не удалось подключиться к базе')
        return False
    return db_name

if not connect_db(db_name):
    sys.exit(-1)
else:
    print('Connection OK')

VUZ = QSqlTableModel()
VUZ.setTable('VUZ')
VUZ.select()

Tp_nir = QSqlTableModel()
Tp_nir.setTable('Tp_nir')
Tp_nir.select()

grntirub = QSqlTableModel()
grntirub.setTable('grntirub')
grntirub.select()

Tp_fv = QSqlTableModel()
Tp_fv.setTable('Tp_fv')
Tp_fv.select()

form.tableView.setSortingEnabled(True)
form.tableView.horizontalHeader().setStretchLastSection(True)
form.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
#form.widget.
form.Tp_nir_redact_widget.setVisible(False)

form.add_confirm_widget.setVisible(False)
form.redact_confirm_widget.setVisible(False)
form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
form.stackedWidget.setCurrentWidget(form.page)

def table_show_VUZ():
    form.tableView.setModel(VUZ)
    form.Tp_nir_redact_widget.setVisible(False)

def table_show_Tp_nir():
    form.tableView.setModel(Tp_nir)
    form.Tp_nir_redact_widget.setVisible(True)

def table_show_grntirub():
    form.tableView.setModel(grntirub)
    form.Tp_nir_redact_widget.setVisible(False)

def table_show_Tp_fv():
    form.tableView.setModel(Tp_fv)
    form.Tp_nir_redact_widget.setVisible(False)

def selectRows():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

def selectColums():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectColumns)

def selectItems():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

def add_widget():
    form.stackedWidget.setCurrentWidget(form.page_add_widget)

def redact_widget():
    form.stackedWidget.setCurrentWidget(form.page_redact_widget)

def close_add_widget():
    form.stackedWidget.setCurrentWidget(form.page)

def close_redact_widget():
    form.stackedWidget.setCurrentWidget(form.page)

def save_add_widget():
    form.add_confirm_widget.setVisible(True)

def save_redact_widget():
    form.redact_confirm_widget.setVisible(True)

def close_add_confirm():
    form.add_confirm_widget.setVisible(False)
    form.stackedWidget.setCurrentWidget(form.page)

def close_redact_confirm():
    form.redact_confirm_widget.setVisible(False)
    form.stackedWidget.setCurrentWidget(form.page)



form.action_show_VUZ.triggered.connect(table_show_VUZ)
form.action_show_Tp_nir.triggered.connect(table_show_Tp_nir)
form.action_show_grntirub.triggered.connect(table_show_grntirub)
form.action_show_Tp_fv.triggered.connect(table_show_Tp_fv)
form.Tp_nir_add_grntiNature_comboBox.addItems(["Прикладное исследование (П)", "Экспериментальная разработка (Р)", "Фундаментальное исследование (Ф)"])
form.Select_rows_action.triggered.connect(selectRows)
form.Select_columns_action.triggered.connect(selectColums)
form.Select_items_action.triggered.connect(selectItems)
form.add_widget_open_pushButton.clicked.connect(add_widget)
form.redact_widget_open_pushButton.clicked.connect(redact_widget)
form.add_widget_close_pushButton.clicked.connect(close_add_widget)
form.redact_widget_close_pushButton.clicked.connect(close_redact_widget)
form.Tp_nir_add_widget_saveButton.clicked.connect(save_add_widget)
form.redact_widget_saveButton.clicked.connect(save_redact_widget)
form.close_add_confirm_pushButton.clicked.connect(close_add_confirm)
form.close_redact_confirm_pushButton.clicked.connect(close_redact_confirm)
form.Tp_nir_add_VUZcode_name_comboBox.addItems([str(i) + ' ' + var for var, i in zip(name_list, code_list)] )


#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()


window.show()
app.exec()