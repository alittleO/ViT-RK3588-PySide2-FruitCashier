from multiprocessing import Process, Queue
import numpy as np
from rknnlite.api import RKNNLite
import time

class InferenceProcess(Process):
    def __init__(self, image_queue, result_queue):
        super(InferenceProcess, self).__init__()
        self.image_queue = image_queue
        self.result_queue = result_queue

    def run(self):
        # 初始化模型
        rknn_lite = RKNNLite()
        rknn_lite.load_rknn('/home/orangepi/Desktop/model/vit.rknn')
        print("模型已加载")

        while True:
            # 从队列中获取图像
            img = self.image_queue.get()
            if img is None:  # 使用None作为停止信号
                print("推理进程接收停止信号")
                break

            # 执行推理
            outputs = rknn_lite.inference([img])
            probabilities = np.exp(outputs[0]) / np.sum(np.exp(outputs[0]), axis=1, keepdims=True)
            max_prob_index = np.argmax(probabilities[0])
            max_prob_value = probabilities[0][max_prob_index]

            # 将结果放入结果队列
            self.result_queue.put((max_prob_index, max_prob_value))
            print("推理结果已输出")

        # 清理资源
        rknn_lite.release()

if __name__ == '__main__':
    image_queue = Queue()
    result_queue = Queue()

    inference_process = InferenceProcess(image_queue, result_queue)
    inference_process.start()

    # 发送一些图像进行推理
    for _ in range(5):
        image = np.random.rand(224, 224, 3).astype(np.float32)
        image_queue.put(image)
        time.sleep(1)  # 模拟推理间隔

    # 发送停止信号
    image_queue.put(None)

    # 读取结果
    while not result_queue.empty():
        result = result_queue.get()
        print("接收到的推理结果:", result)

    inference_process.join()
    print("推理进程已正常结束")
