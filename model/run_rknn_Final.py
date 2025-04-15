import cv2
import numpy as np
import platform
from synset_label import labels  # 导入标签
from rknnlite.api import RKNNLite
import time

# 兼容的设备节点路径
DEVICE_COMPATIBLE_NODE = '/proc/device-tree/compatible'

# 获取当前运行的主机类型
def get_host():
    # 获取操作系统类型和机器类型
    system = platform.system()
    machine = platform.machine()
    os_machine = system + '-' + machine
    if os_machine == 'Linux-aarch64':
        try:
            with open(DEVICE_COMPATIBLE_NODE) as f:
                device_compatible_str = f.read()
                # 根据设备兼容性字符串判断是哪种RK设备
                if 'rk3588' in device_compatible_str:
                    host = 'RK3588'
                elif 'rk3562' in device_compatible_str:
                    host = 'RK3562'
                else:
                    host = 'RK3566_RK3568'
        except IOError:
            print('读取设备节点 {} 失败。'.format(DEVICE_COMPATIBLE_NODE))
            exit(-1)
    else:
        host = os_machine
    return host

INPUT_SIZE = 224

# 根据不同设备指定的RKNN模型路径
RK3566_RK3568_RKNN_MODEL = 'resnet18_for_rk3566_rk3568.rknn'
RK3588_RKNN_MODEL = 'resnet18_for_rk3588.rknn'
RK3562_RKNN_MODEL = 'resnet18_for_rk3562.rknn'


if __name__ == '__main__':

    # 获取设备信息
    host_name = get_host()
    if host_name == 'RK3566_RK3568':
        rknn_model = RK3566_RK3568_RKNN_MODEL
    elif host_name == 'RK3562':
        rknn_model = RK3562_RKNN_MODEL
    elif host_name == 'RK3588':
        rknn_model = RK3588_RKNN_MODEL
    else:
        print("此演示无法在当前平台上运行: {}".format(host_name))
        exit(-1)

    rknn_lite = RKNNLite()

    # 加载RKNN模型
    print('--> 加载RKNN模型')
    model_path = '/home/orangepi/Desktop/model/vit.rknn'
    ###model_path = '/home/orangepi/Desktop/rknn_toolkit_lite2/examples/resnet18/resnet18_for_rk3588.rknn'
    ret = rknn_lite.load_rknn(model_path)#(rknn_model)
    if ret != 0:
        print('加载RKNN模型失败')
        exit(ret)
    print('完成')

    #ori_img = cv2.imread('/home/orangepi/Desktop/testimg/xihongshi.png')
    #ori_img = cv2.imread('/home/orangepi/Desktop/xihongshi224.png')
    ori_img = cv2.imread('/home/orangepi/Desktop/capture.jpg')
    img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, 0)

    # 初始化运行环境
    print('--> 初始化运行环境')
    if host_name == 'RK3588':
        # 对于RK3588, 通过core_mask参数指定模型在哪个NPU核心上运行
        ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)
    else:
        ret = rknn_lite.init_runtime()
    if ret != 0:
        print('初始化运行环境失败')
        exit(ret)
    print('完成')

    # 执行模型推理
    start_time = time.perf_counter()
    print('--> 运行模型')
    outputs = rknn_lite.inference(inputs=[img])
    #print(outputs)

    # 测量推理时间
    end_time = time.perf_counter()

    # 计算用时
    inference_time = (end_time - start_time) * 1000  # 转换为毫秒

    # 打印用时
    print('推理用时: {:.2f} ms'.format(inference_time))


    # 展示分类结果

    print('完成')

    logits = outputs[0]#np.array(result)

    # 应用 softmax
    probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)

    # id2label 字典
    id2label = {
        "0": "apple", "1": "banana", "10": "cucumber", "11": "eggplant", "12": "garlic",
        "13": "ginger", "14": "grapes", "15": "jalepeno", "16": "kiwi", "17": "lemon",
        "18": "lettuce", "19": "mango", "2": "beetroot", "20": "onion", "21": "orange",
        "22": "paprika", "23": "pear", "24": "peas", "25": "pineapple", "26": "pomegranate",
        "27": "potato", "28": "raddish", "29": "soy beans", "3": "bell pepper",
        "30": "spinach", "31": "sweetcorn", "32": "sweetpotato", "33": "tomato",
        "34": "turnip", "35": "watermelon", "4": "cabbage", "5": "capsicum", "6": "carrot",
        "7": "cauliflower", "8": "chilli pepper", "9": "corn"
    }

    # 创建类别和概率的列表
    class_probabilities = [(id2label[str(i)], prob) for i, prob in enumerate(probabilities[0])]

    # 按概率从大到小排序
    sorted_probabilities = sorted(class_probabilities, key=lambda x: x[1], reverse=True)

    # 打印排序后的类别和概率
    for label, prob in sorted_probabilities:
        print(f"{label}: {prob:.6f}")
    # 释放资源
    rknn_lite.release()
    
