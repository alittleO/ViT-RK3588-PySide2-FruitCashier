import cv2
import numpy as np
import time
from rknnlite.api import RKNNLite

def init_rknn(model_path, core_mask=RKNNLite.NPU_CORE_0):
    """
    初始化RKNN模型和运行环境。

    参数:
        model_path (str): RKNN模型文件的路径。
        core_mask (int): 指定RKNNLite使用的NPU核心。

    返回:
        rknn_lite (RKNNLite): 初始化后的RKNNLite对象，准备用于推理。
    """
    rknn_lite = RKNNLite()
    ret = rknn_lite.load_rknn(model_path)
    if ret != 0:
        print('加载RKNN模型失败')
        exit(ret)

    ret = rknn_lite.init_runtime(core_mask=core_mask)
    if ret != 0:
        print('初始化运行环境失败')
        exit(ret)

    return rknn_lite
