
import numpy as np

from rknnlite.api import RKNNLite

def run_rknn(rknn_lite, img):
    """
    运行模型推理并返回概率大于0.4的结果，如果没有结果概率大于0.4，返回概率最大的结果。

    参数:
        rknn_lite (RKNNLite): 初始化后的RKNNLite对象。
        image_path (str): 输入图像的路径。

    返回:
        high_prob_results (list): 概率大于0.4的类别和其概率或者概率最大的结果。
    """
    # 执行模型推理
    outputs = rknn_lite.inference(inputs=[img])

    # 检查模型推理是否成功
    if outputs is None:
        print("模型推理失败，未能获取任何输出。")
        return []

    logits = outputs[0]
    probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)

    # 筛选高概率结果
    high_prob_results = [(str(i), prob) for i, prob in enumerate(probabilities[0]) if prob > 0.15]

    # 如果没有高概率结果，返回概率最大的结果
    if not high_prob_results:
        max_prob_index = np.argmax(probabilities[0])
        max_prob_value = probabilities[0][max_prob_index]
        print(f"没有识别到概率大于0.4的结果，返回概率最大的结果: 类别 {max_prob_index}, 概率 {max_prob_value}")
        if max_prob_value > 0.15:
            return [(str(max_prob_index), max_prob_value)]
        else:
            return []
        
    #for label, prob in high_prob_results:
        #print(f"识别到: 类别 {label}, 概率 {prob}")
        
    #print("---------------------------------")

    return high_prob_results


    '''    # 映射ID到标签
    id2label = {
    "0": "苹果", "1": "香蕉", "10": "黄瓜", "11": "茄子", "12": "大蒜",
    "13": "姜", "14": "葡萄", "15": "墨西哥牛角椒", "16": "猕猴桃", "17": "柠檬",
    "18": "生菜", "19": "芒果", "2": "甜菜根", "20": "洋葱", "21": "橙子",
    "22": "鲜甜椒", "23": "梨", "24": "豌豆", "25": "菠萝", "26": "石榴",
    "27": "土豆", "28": "萝卜", "29": "黄豆", "3": "彩椒",
    "30": "菠菜", "31": "甜玉米", "32": "甘薯", "33": "番茄",
    "34": "芜菁", "35": "西瓜", "4": "卷心菜", "5": "甜椒", "6": "胡萝卜",
    "7": "花椰菜", "8": "辣椒", "9": "玉米"
    }'''