import sys  # 导入系统模块
import cv2  # 导入OpenCV库
import numpy as np
from PySide2.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTableWidget, QListWidget, QGridLayout, 
                               QFrame, QSizePolicy, QHeaderView, QTableWidgetItem, 
                               QMessageBox, QDialogButtonBox, QDialog, QComboBox)  
from PySide2.QtGui import QPixmap, QImage, QFont  
from PySide2.QtCore import Qt, QThread, Signal,  QTimer  

from init_rknn import init_rknn  
from run_rknn import run_rknn 
from id2label import id2label, id2price, enlabels

import serial
import threading
from multiprocessing import Process, Queue






