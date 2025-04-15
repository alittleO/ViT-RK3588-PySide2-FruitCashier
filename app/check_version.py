import sys
import cv2
import numpy as np
import PySide2
import serial
import threading
import multiprocessing

# 输出各个库的版本
print("Python version:", sys.version)
print("OpenCV version:", cv2.__version__)
print("NumPy version:", np.__version__)
print("PySide2 version:", PySide2.__version__)
print("pyserial version:", serial.VERSION)
print("threading (built-in, no version)")
print("multiprocessing (built-in, no version)")
