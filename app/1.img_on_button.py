import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import QSize, Qt

def create_button(parent, button_text, image_path):
    # 创建一个按钮并命名
    button = QPushButton(button_text, parent)
    button.setGeometry(50, 50, 220, 180)  # 调整按钮大小

    # 设置按钮样式，包括圆角、背景颜色以及点击时的颜色
    button.setStyleSheet(
        "QPushButton {"
        "border: 2px solid #8f8f91;"
        "border-radius: 20px;"  # 增大圆角
        "background-color: #f3f3f3;"
        "}"
        "QPushButton:pressed {"
        "background-color: #ADD8E6;"  # 设置按钮被按下时的颜色为浅蓝色
        "}"
    )

    # 创建一个垂直布局
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)  # 设置内容竖向居中

    # 添加文本标签“香蕉”并设置居中
    label_banana = QLabel('香蕉', parent)
    label_banana.setAlignment(Qt.AlignCenter)  # 设置文本居中
    layout.addWidget(label_banana)

    # 添加图片
    label_image = QLabel(parent)
    pixmap = QPixmap(image_path)  # 图片路径
    label_image.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio))  # 调整图片大小
    layout.addWidget(label_image)

    # 添加文本标签“单价”并设置居中
    label_price = QLabel('单价', parent)
    label_price.setAlignment(Qt.AlignCenter)  # 设置文本居中
    layout.addWidget(label_price)

    # 将布局设置到按钮中
    button.setLayout(layout)

    # 连接按钮的点击事件
    button.clicked.connect(lambda: QMessageBox.information(parent, 'Button Name', button.text()))

    return button

class Example(QWidget):
    def __init__(self):
        super().__init__()

        # 调用封装的函数创建多个按钮
        create_button(self, '按钮一', '/home/orangepi/Desktop/temp.jpg')
        create_button(self, '按钮二', '/home/orangepi/Desktop/temp.jpg').move(50, 250)  # 移动位置

        # 设置窗口
        self.setGeometry(300, 300, 320, 500)  # 调整窗口大小以适应多个按钮
        self.setWindowTitle('PySide2 Multiple Buttons')
        self.show()

# 创建应用实例
app = QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())
