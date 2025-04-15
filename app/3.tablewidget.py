from PySide2.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QLabel

def add_data(table, data):
    row_index = table.rowCount()
    table.insertRow(row_index)
    for column_index, item in enumerate(data):
        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))
    update_totals(table)  # 更新总金额和总项数

def remove_last_item(table):
    if table.rowCount() > 0:
        table.removeRow(table.rowCount() - 1)
    update_totals(table)  # 更新总金额和总项数

def clear_data(table):
    table.setRowCount(0)
    update_totals(table)  # 更新总金额和总项数

def calculate_total(table):
    total = 0
    for row in range(table.rowCount()):
        total += float(table.item(row, 3).text())
    return total

def update_totals(table):
    total = calculate_total(table)  # 使用 calculate_total 函数计算总金额
    total_items = table.rowCount()  # 获取表格的行数作为总项数
    label_total.setText(f"总金额: {total}")  # 更新金额总计标签
    label_total_items.setText(f"总项数: {total_items}")  # 更新总项数标签

app = QApplication([])

# 创建主窗口和布局
window = QWidget()
layout = QVBoxLayout()

# 创建表格
table = QTableWidget(0, 4)
table.setHorizontalHeaderLabels(["商品", "单价", "数量", "小计"])
layout.addWidget(table)

# 添加按钮和它们的功能
btn_add = QPushButton("添加数据")
btn_add.clicked.connect(lambda: add_data(table, ["橙子", "4.00", "20", "80.00"]))
layout.addWidget(btn_add)

btn_remove_last = QPushButton("删除最后一项")
btn_remove_last.clicked.connect(lambda: remove_last_item(table))
layout.addWidget(btn_remove_last)

btn_clear = QPushButton("清空列表")
btn_clear.clicked.connect(lambda: clear_data(table))
layout.addWidget(btn_clear)

# 总计标签和总项数标签
label_total = QLabel("总金额: 0")
label_total_items = QLabel("总项数: 0")
layout.addWidget(label_total)
layout.addWidget(label_total_items)

# 设置窗口布局和显示
window.setLayout(layout)
window.show()

app.exec_()
