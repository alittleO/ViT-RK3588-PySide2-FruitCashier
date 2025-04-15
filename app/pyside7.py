import sys
from PySide2.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                               QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget,
                               QTableWidgetItem, QHeaderView)

class Ui(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 设置整体布局
        main_layout = QHBoxLayout(self)

        # 左侧部分
        left_layout = QVBoxLayout()

        # 上方按钮组
        button_layout = QHBoxLayout()
        button1 = QPushButton("香蕉")
        button2 = QPushButton("苹果")
        button_layout.addWidget(button1)
        button_layout.addWidget(button2)

        # 中间显示区
        display_area = QLabel("感应区\n888.88kg")
        display_area.setStyleSheet("border: 1px solid gray;")

        # 下方按钮组
        operation_layout = QHBoxLayout()
        clear_button = QPushButton("清空")
        delete_button = QPushButton("删除")
        operation_layout.addWidget(clear_button)
        operation_layout.addWidget(delete_button)

        # 将上方、中间、下方组件加入左侧布局
        left_layout.addLayout(button_layout)
        left_layout.addWidget(display_area, 1)  # 1表示该控件会在纵向拉伸时占据更多空间
        left_layout.addLayout(operation_layout)

        # 右侧的商品列表
        right_layout = QVBoxLayout()
        product_table = QTableWidget(10, 5)
        product_table.setHorizontalHeaderLabels(["序号", "商品名", "单价", "重量", "小计"])
        header = product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # 让表格列宽适应内容大小

        # 将商品列表加入右侧布局
        right_layout.addWidget(product_table)

        # 将左侧和右侧布局加入主布局
        main_layout.addLayout(left_layout, 2)  # 数字代表布局占比，2是左侧，3是右侧
        main_layout.addLayout(right_layout, 3)

        # 设置窗口
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('购物界面')

# 主程序
app = QApplication(sys.argv)
ui = Ui()
ui.show()
sys.exit(app.exec_())
