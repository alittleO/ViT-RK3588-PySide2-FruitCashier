import cv2
import numpy as np
import time
from rknnlite.api import RKNNLite

# 模型路径

INPUT_SIZE = 224

if __name__ == '__main__':

    rknn_lite = RKNNLite()

    # 加载RKNN模型
    print('--> 加载RKNN模型')
    model_path = '/home/orangepi/Desktop/model/vit.rknn'  # 请确保此路径正确
    ret = rknn_lite.load_rknn(model_path)
    if ret != 0:
        print('加载RKNN模型失败')
        exit(ret)
    print('完成')

    # 读取图片
    ori_img = cv2.imread('/home/orangepi/Desktop/capture.jpg')
    img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, 0)

    # 初始化运行环境
    print('--> 初始化运行环境')
    ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)  # 为RK3588指定NPU核心
    if ret != 0:
        print('初始化运行环境失败')
        exit(ret)
    print('完成')

    # 执行模型推理
    start_time = time.perf_counter()
    print('--> 运行模型')
    outputs = rknn_lite.inference(inputs=[img])
    end_time = time.perf_counter()

    # 计算用时
    inference_time = (end_time - start_time) * 1000  # 转换为毫秒
    print('推理用时: {:.2f} ms'.format(inference_time))
    print('完成')

    logits = outputs[0]
    probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)

    id2label = {
    "0": "苹果", "1": "香蕉", "10": "黄瓜", "11": "茄子", "12": "大蒜",
    "13": "姜", "14": "葡萄", "15": "墨西哥牛角椒", "16": "猕猴桃", "17": "柠檬",
    "18": "生菜", "19": "芒果", "2": "甜菜根", "20": "洋葱", "21": "橙子",
    "22": "鲜甜椒", "23": "梨", "24": "豌豆", "25": "菠萝", "26": "石榴",
    "27": "土豆", "28": "萝卜", "29": "黄豆", "3": "彩椒",
    "30": "菠菜", "31": "甜玉米", "32": "甘薯", "33": "番茄",
    "34": "芜菁", "35": "西瓜", "4": "卷心菜", "5": "甜椒", "6": "胡萝卜",
    "7": "花椰菜", "8": "辣椒", "9": "玉米"
    }


    # 创建类别和概率的列表
    class_probabilities = [(id2label[str(i)], prob) for i, prob in enumerate(probabilities[0])]
    sorted_probabilities = sorted(class_probabilities, key=lambda x: x[1], reverse=True)

    # 打印排序后的类别和概率
    for label, prob in sorted_probabilities:
        print(f"{label}: {prob:.6f}")

    # 释放资源
    rknn_lite.release()
