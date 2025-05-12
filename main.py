import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QDialog, QComboBox, QListWidgetItem, QInputDialog)
from PyQt5.QtCore import Qt


class Slot:
    def __init__(self, name, slot_type, inheritance, data=None):
        self.name = name
        self.type = slot_type
        self.inheritance = inheritance
        self.data = datas


class Frame:
    def __init__(self, name):
        self.name = name
        self.slots = []

    def add_slot(self, slot):
        self.slots.append(slot)

    def get_slot(self, name):
        for slot in self.slots:
            if slot.name == name:
                return slot
        return None

    def remove_slot(self, name):
        self.slots = [s for s in self.slots if s.name != name]


class LispProcedure:
    def execute(self):
        pass


class PrintLisp(LispProcedure):
    def __init__(self, text):
        self.text = text

    def execute(self):
        return self.text


class FindLisp(LispProcedure):
    def __init__(self, characteristics):
        self.characteristics = characteristics
        self.database = None
        self.root_frame = None

    def set_database(self, database):
        self.database = database

    def set_root_frame(self, frame_name):
        self.root_frame = frame_name

    def execute(self):
        for frame_name, frame in self.database.items():
            if frame_name == self.root_frame:
                continue
            for slot in frame.slots:
                if slot.type == "PRINT":
                    return frame_name
        return "NOT_FOUND_FRAME"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.frames = {}
        self.lisp_procedures = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Frames Knowledge System")
        self.setGeometry(100, 100, 800, 600)


        self.frames_list = QListWidget()
        self.frame_info = QListWidget()
        self.frame_name_label = QLabel("Selected Frame: None")


        self.add_frame_btn = QPushButton("Add Frame")
        self.delete_frame_btn = QPushButton("Delete Frame")
        self.add_slot_btn = QPushButton("Add Slot")
        self.delete_slot_btn = QPushButton("Delete Slot")
        self.add_lisp_btn = QPushButton("Add Lisp")
        self.run_procedure_btn = QPushButton("Run Procedure")


        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Frames:"))
        left_panel.addWidget(self.frames_list)
        left_panel.addWidget(self.add_frame_btn)
        left_panel.addWidget(self.delete_frame_btn)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.frame_name_label)
        right_panel.addWidget(QLabel("Frame Info:"))
        right_panel.addWidget(self.frame_info)
        right_panel.addWidget(self.add_slot_btn)
        right_panel.addWidget(self.delete_slot_btn)
        right_panel.addWidget(self.add_lisp_btn)
        right_panel.addWidget(self.run_procedure_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_panel, 40)
        main_layout.addLayout(right_panel, 60)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


        self.add_frame_btn.clicked.connect(self.add_frame)
        self.delete_frame_btn.clicked.connect(self.delete_frame)
        self.add_slot_btn.clicked.connect(self.show_add_slot_dialog)
        self.delete_slot_btn.clicked.connect(self.delete_slot)
        self.add_lisp_btn.clicked.connect(self.show_add_lisp_dialog)
        self.run_procedure_btn.clicked.connect(self.run_procedure)
        self.frames_list.itemClicked.connect(self.show_frame_info)

    def add_frame(self):
        name, ok = QInputDialog.getText(self, "Add Frame", "Enter frame name:")
        if ok and name:
            if name in self.frames:
                QMessageBox.warning(self, "Error", "Frame already exists!")
                return
            self.frames[name] = Frame(name)
            self.frames_list.addItem(name)

    def delete_frame(self):
        current_item = self.frames_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "No frame selected!")
            return

        frame_name = current_item.text()
        del self.frames[frame_name]
        self.frames_list.takeItem(self.frames_list.row(current_item))
        self.frame_info.clear()
        self.frame_name_label.setText("Selected Frame: None")

    def show_frame_info(self, item):
        frame_name = item.text()
        self.frame_name_label.setText(f"Selected Frame: {frame_name}")
        self.frame_info.clear()

        frame = self.frames[frame_name]
        for slot in frame.slots:
            item = QListWidgetItem(f"{slot.name} | {slot.type} | {slot.inheritance} | {slot.data}")
            self.frame_info.addItem(item)

    def show_add_slot_dialog(self):
        current_item = self.frames_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Select a frame first!")
            return

        dialog = SlotAddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            slot_data = dialog.get_data()
            frame_name = current_item.text()
            new_slot = Slot(*slot_data)
            self.frames[frame_name].add_slot(new_slot)
            self.show_frame_info(current_item)

    def delete_slot(self):
        frame_item = self.frames_list.currentItem()
        slot_item = self.frame_info.currentItem()

        if not frame_item or not slot_item:
            QMessageBox.warning(self, "Error", "Select both frame and slot!")
            return

        frame_name = frame_item.text()
        slot_name = slot_item.text().split(" | ")[0]
        self.frames[frame_name].remove_slot(slot_name)
        self.show_frame_info(frame_item)

    def show_add_lisp_dialog(self):
        current_item = self.frames_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Select a frame first!")
            return

        dialog = AddLispDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, lisp_type, data = dialog.get_data()
            frame_name = current_item.text()

            if lisp_type == "PRINT":
                self.lisp_procedures[name] = PrintLisp(data)
                slot_type = "LISP"
                slot_data = "PRINT"
            else:  # FIND
                characteristics = data.split(",")
                self.lisp_procedures[name] = FindLisp(characteristics)
                slot_type = "LISP"
                slot_data = "FIND"

            new_slot = Slot(name, slot_type, "Unique", slot_data)
            self.frames[frame_name].add_slot(new_slot)
            self.show_frame_info(current_item)

    def run_procedure(self):
        frame_item = self.frames_list.currentItem()
        slot_item = self.frame_info.currentItem()

        if not frame_item or not slot_item:
            QMessageBox.warning(self, "Error", "Select both frame and slot!")
            return

        slot_name = slot_item.text().split(" | ")[0]
        if slot_name not in self.lisp_procedures:
            QMessageBox.warning(self, "Error", "Selected slot is not a procedure!")
            return

        procedure = self.lisp_procedures[slot_name]

        if isinstance(procedure, PrintLisp):
            QMessageBox.information(self, "Procedure Result", procedure.execute())
        elif isinstance(procedure, FindLisp):
            procedure.set_database(self.frames)
            procedure.set_root_frame(frame_item.text())
            result = procedure.execute()

            if result == "NOT_FOUND_FRAME":
                QMessageBox.warning(self, "Result", "No matching frame found!")
            else:
                result_text = self.lisp_procedures.get(result, PrintLisp("No description available")).execute()
                QMessageBox.information(self, "Procedure Result",
                                        f"Found frame: {result}\nDescription: {result_text}")



class SlotAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Slot")
        self.setModal(True)

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["FRAME", "BOOL", "TEXT"])
        self.inheritance_combo = QComboBox()
        self.inheritance_combo.addItems(["Unique", "Same"])
        self.data_edit = QLineEdit()

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Slot Name:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Slot Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Inheritance:"))
        layout.addWidget(self.inheritance_combo)
        layout.addWidget(QLabel("Data (optional):"))
        layout.addWidget(self.data_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return (
            self.name_edit.text(),
            self.type_combo.currentText(),
            self.inheritance_combo.currentText(),
            self.data_edit.text() if self.data_edit.text() else None
        )


class AddLispDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Lisp Procedure")
        self.setModal(True)

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["PRINT", "FIND"])
        self.data_edit = QTextEdit()

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Procedure Name:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Procedure Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Data (text for PRINT, comma-separated for FIND):"))
        layout.addWidget(self.data_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return (
            self.name_edit.text(),
            self.type_combo.currentText(),
            self.data_edit.toPlainText()
        )



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
