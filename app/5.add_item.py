import sys
from PySide2.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
                               QDialog, QComboBox, QLabel, QDialogButtonBox, QLineEdit)

# 从外部文件引入 id2label 和 id2price 字典
from id2label import id2label, id2price

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super(AddItemDialog, self).__init__(parent)
        self.setWindowTitle("选择果蔬")
        self.layout = QVBoxLayout()

        self.label = QLabel("选择要添加的商品：")
        self.combo_box = QComboBox()
        self.populate_combobox()
        self.combo_box.currentIndexChanged.connect(self.update_display_info)

        self.info_label = QLabel("单价：0 元\n重量：0 公斤\n总价：0 元")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def populate_combobox(self):
        for id, label in id2label.items():
            self.combo_box.addItem(label, id)

    def get_selected_item(self):
        return self.combo_box.currentData()  # 返回当前选中的序号

    def update_display_info(self):
        item_id = self.get_selected_item()
        price = id2price[item_id]
        current_weight = 2.5  # 假设重量
        total_price = price * current_weight
        self.info_label.setText(f"单价：{price} 元\n重量：{current_weight} 公斤\n总价：{total_price} 元")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("商品列表")
        self.table = []

        self.add_button = QPushButton("添加商品")
        self.add_button.clicked.connect(self.show_add_item_dialog)

        layout = QVBoxLayout()
        widget = QWidget()
        layout.addWidget(self.add_button)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec_():
            selected_id = dialog.get_selected_item()
            self.add_data(selected_id)

    def add_data(self, item_id):
        commodity = id2label[item_id]
        price = id2price[item_id]
        current_weight = 2.5  # 假设重量
        total_price = price * current_weight
        entry = [commodity, str(price), str(round(current_weight, 3)),
                 str(round(total_price, 2))]
        self.table.append(entry)
        print(f"商品：{entry[0]}, 单价：{entry[1]}元, 重量：{entry[2]}公斤, 总价：{entry[3]}元")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
