import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QDialog, QComboBox, QListWidgetItem, QInputDialog)
from PyQt5.QtCore import Qt


class Demon:
    def execute(self, frame, slot):
        pass


class IfNeededDemon(Demon):
    def __init__(self, procedure):
        self.procedure = procedure

    def execute(self, frame, slot):
        return self.procedure.execute(frame, slot)


class IfAddedDemon(Demon):
    def __init__(self, procedure):
        self.procedure = procedure

    def execute(self, frame, slot):
        return self.procedure.execute(frame, slot)


class Slot:
    def __init__(self, name, slot_type, inheritance="Unique", data=None,
                 if_needed=None, if_added=None):
        self.name = name
        self.type = slot_type  # FRAME, BOOL, TEXT, LISP
        self.inheritance = inheritance  # Unique, Same
        self._data = data
        self.if_needed = if_needed
        self.if_added = if_added

    @property
    def data(self):
        if self.if_needed and self._data is None:
            return self.if_needed.execute(None, self)
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        if self.if_added:
            self.if_added.execute(None, self)


class Frame:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.slots = []

    def add_slot(self, slot):
        existing = self.get_slot(slot.name)
        if existing:
            self.slots.remove(existing)
        self.slots.append(slot)

    def get_slot(self, name):
        for slot in self.slots:
            if slot.name == name:
                return slot

        # Проверка наследования от родителя
        if self.parent:
            return self.parent.get_slot(name)
        return None

    def get_slot_value(self, name):
        slot = self.get_slot(name)
        if slot:
            return slot.data
        return None

    def set_slot_value(self, name, value):
        slot = self.get_slot(name)
        if slot:
            slot.data = value
        else:
            new_slot = Slot(name, "TEXT", "Unique", value)
            self.add_slot(new_slot)


class LispProcedure:
    def execute(self, frame, slot):
        pass


class PrintLisp(LispProcedure):
    def __init__(self, text):
        self.text = text

    def execute(self, frame, slot):
        return self.text


class FindLisp(LispProcedure):
    def __init__(self, conditions):
        self.conditions = conditions

    def execute(self, frame, slot):
        results = []
        for condition in self.conditions:
            parts = condition.split("=")
            if len(parts) == 2:
                slot_name, value = parts
                slot_value = frame.get_slot_value(slot_name)
                if str(slot_value) != value:
                    return None
        return frame.name


class FrameSystem:
    def __init__(self):
        self.frames = {}
        self.procedures = {}

    def add_frame(self, name, parent_name=None):
        parent = self.frames.get(parent_name) if parent_name else None
        frame = Frame(name, parent)
        self.frames[name] = frame
        return frame

    def find_frames(self, conditions):
        results = []
        for frame in self.frames.values():
            match = True
            for condition in conditions:
                parts = condition.split("=")
                if len(parts) == 2:
                    slot_name, value = parts
                    slot_value = frame.get_slot_value(slot_name)
                    if str(slot_value) != value:
                        match = False
                        break
            if match:
                results.append(frame.name)
        return results


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.system = FrameSystem()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Frame Knowledge System")
        self.setGeometry(100, 100, 900, 600)

        # Основные виджеты
        self.frames_list = QListWidget()
        self.slots_list = QListWidget()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        # Кнопки управления
        self.add_frame_btn = QPushButton("Add Frame")
        self.del_frame_btn = QPushButton("Delete Frame")
        self.add_slot_btn = QPushButton("Add Slot")
        self.del_slot_btn = QPushButton("Delete Slot")
        self.add_proc_btn = QPushButton("Add Procedure")
        self.search_btn = QPushButton("Search")

        # Компоновка
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Frames:"))
        left_panel.addWidget(self.frames_list)
        left_panel.addWidget(self.add_frame_btn)
        left_panel.addWidget(self.del_frame_btn)

        center_panel = QVBoxLayout()
        center_panel.addWidget(QLabel("Slots:"))
        center_panel.addWidget(self.slots_list)
        center_panel.addWidget(self.add_slot_btn)
        center_panel.addWidget(self.del_slot_btn)
        center_panel.addWidget(self.add_proc_btn)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Information:"))
        right_panel.addWidget(self.info_text)
        right_panel.addWidget(self.search_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_panel, 30)
        main_layout.addLayout(center_panel, 30)
        main_layout.addLayout(right_panel, 40)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Подключение сигналов
        self.add_frame_btn.clicked.connect(self.add_frame_dialog)
        self.del_frame_btn.clicked.connect(self.delete_frame)
        self.add_slot_btn.clicked.connect(self.add_slot_dialog)
        self.del_slot_btn.clicked.connect(self.delete_slot)
        self.add_proc_btn.clicked.connect(self.add_procedure_dialog)
        self.search_btn.clicked.connect(self.search_dialog)
        self.frames_list.itemClicked.connect(self.update_slots_list)
        self.slots_list.itemClicked.connect(self.show_slot_info)

        self.update_frames_list()

    def update_frames_list(self):
        self.frames_list.clear()
        for frame_name in self.system.frames:
            self.frames_list.addItem(frame_name)

    def update_slots_list(self, item):
        self.slots_list.clear()
        frame_name = item.text()
        frame = self.system.frames[frame_name]

        for slot in frame.slots:
            item_text = f"{slot.name} ({slot.type})"
            if slot.inheritance == "Same":
                item_text += " [Same]"
            self.slots_list.addItem(item_text)

    def show_slot_info(self, item):
        frame_item = self.frames_list.currentItem()
        if not frame_item:
            return

        frame_name = frame_item.text()
        slot_name = item.text().split(" ")[0]
        frame = self.system.frames[frame_name]
        slot = frame.get_slot(slot_name)

        info = f"Slot: {slot.name}\n"
        info += f"Type: {slot.type}\n"
        info += f"Inheritance: {slot.inheritance}\n"
        info += f"Value: {slot.data}\n"

        if slot.if_needed:
            info += "\nIF-NEEDED procedure attached\n"
        if slot.if_added:
            info += "\nIF-ADDED procedure attached\n"

        self.info_text.setPlainText(info)

    def add_frame_dialog(self):
        name, ok = QInputDialog.getText(self, "Add Frame", "Frame name:")
        if not ok or not name:
            return

        if name in self.system.frames:
            QMessageBox.warning(self, "Error", "Frame already exists!")
            return

        parent, ok = QInputDialog.getItem(self, "Parent Frame",
                                          "Select parent frame (optional):",
                                          [""] + list(self.system.frames.keys()),
                                          0, False)
        if not ok:
            return

        parent = parent if parent else None
        self.system.add_frame(name, parent)
        self.update_frames_list()

    def delete_frame(self):
        current = self.frames_list.currentItem()
        if not current:
            return

        frame_name = current.text()

        # Проверка на использование как родителя
        used_as_parent = any(f.parent and f.parent.name == frame_name
                             for f in self.system.frames.values())

        if used_as_parent:
            QMessageBox.warning(self, "Error",
                                "Cannot delete frame used as parent!")
            return

        del self.system.frames[frame_name]
        self.update_frames_list()
        self.slots_list.clear()
        self.info_text.clear()

    def add_slot_dialog(self):
        frame_item = self.frames_list.currentItem()
        if not frame_item:
            QMessageBox.warning(self, "Error", "Select a frame first!")
            return

        dialog = SlotDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, slot_type, inheritance, value = dialog.get_data()
            frame = self.system.frames[frame_item.text()]

            # Проверка на существующий слот
            existing = frame.get_slot(name)
            if existing and existing.inheritance == "Same":
                QMessageBox.warning(self, "Error",
                                    "Cannot override Same inherited slot!")
                return

            frame.add_slot(Slot(name, slot_type, inheritance, value))
            self.update_slots_list(frame_item)

    def delete_slot(self):
        frame_item = self.frames_list.currentItem()
        slot_item = self.slots_list.currentItem()
        if not frame_item or not slot_item:
            return

        frame_name = frame_item.text()
        slot_name = slot_item.text().split(" ")[0]
        frame = self.system.frames[frame_name]

        # Удаляем только если слот принадлежит именно этому фрейму
        for slot in frame.slots:
            if slot.name == slot_name:
                frame.slots.remove(slot)
                break

        self.update_slots_list(frame_item)
        self.info_text.clear()

    def add_procedure_dialog(self):
        frame_item = self.frames_list.currentItem()
        slot_item = self.slots_list.currentItem()
        if not frame_item or not slot_item:
            QMessageBox.warning(self, "Error", "Select frame and slot first!")
            return

        frame_name = frame_item.text()
        slot_name = slot_item.text().split(" ")[0]
        frame = self.system.frames[frame_name]
        slot = frame.get_slot(slot_name)

        dialog = ProcedureDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            proc_type, proc_data = dialog.get_data()

            if proc_type == "PRINT":
                proc = PrintLisp(proc_data)
                lisp_proc = LispProcedure()
                lisp_proc.execute = lambda f, s: proc.execute(f, s)
            else:  # FIND
                conditions = [c.strip() for c in proc_data.split(",")]
                proc = FindLisp(conditions)
                lisp_proc = LispProcedure()
                lisp_proc.execute = lambda f, s: proc.execute(f, s)

            demon_type = dialog.get_demon_type()
            if demon_type == "IF-NEEDED":
                slot.if_needed = IfNeededDemon(lisp_proc)
            elif demon_type == "IF-ADDED":
                slot.if_added = IfAddedDemon(lisp_proc)

            self.system.procedures[f"{frame_name}.{slot_name}"] = lisp_proc
            self.show_slot_info(slot_item)

    def search_dialog(self):
        query, ok = QInputDialog.getText(self, "Search",
                                         "Enter search conditions (format: slot=value,...):")
        if not ok or not query:
            return

        conditions = [cond.strip() for cond in query.split(",")]
        results = self.system.find_frames(conditions)

        if not results:
            QMessageBox.information(self, "Search Results", "No frames found")
        else:
            QMessageBox.information(self, "Search Results",
                                    f"Found frames:\n{', '.join(results)}")


class SlotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Slot")

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["FRAME", "BOOL", "TEXT", "LISP"])
        self.inheritance_combo = QComboBox()
        self.inheritance_combo.addItems(["Unique", "Same"])
        self.value_edit = QLineEdit()

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Slot Name:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Slot Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Inheritance:"))
        layout.addWidget(self.inheritance_combo)
        layout.addWidget(QLabel("Initial Value:"))
        layout.addWidget(self.value_edit)

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
            self.value_edit.text()
        )


class ProcedureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Procedure")

        self.type_combo = QComboBox()
        self.type_combo.addItems(["PRINT", "FIND"])
        self.demon_combo = QComboBox()
        self.demon_combo.addItems(["IF-NEEDED", "IF-ADDED"])
        self.data_edit = QTextEdit()

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Procedure Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Demon Type:"))
        layout.addWidget(self.demon_combo)
        layout.addWidget(QLabel("Procedure Data:"))
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
            self.type_combo.currentText(),
            self.data_edit.toPlainText()
        )

    def get_demon_type(self):
        return self.demon_combo.currentText()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
