import cv2
import numpy as np
from init_rknn import init_rknn
from run_rknn import run_rknn

def main():
    # 模型路径和图片路径
    model_path = '/home/orangepi/Desktop/model/vit.rknn'
    image_path = '/home/orangepi/Desktop/capture.jpg'
    
    # 初始化模型
    print("Initializing RKNN model...")
    rknn_lite = init_rknn(model_path)
    
    ori_img = cv2.imread(image_path)
    img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, 0)
    # 运行模型推理
    results = run_rknn(rknn_lite, img)
    
    print(type(results))
    print(results)
    # 打印推理结果
    print("Inference Results:")
    for i, prob in results:
        print(f"{i}: {prob:.6f}")

if __name__ == '__main__':
    main()
