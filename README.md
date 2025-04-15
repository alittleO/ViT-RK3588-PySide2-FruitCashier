# ViT-RK3588-PySide2-FruitCashier

这是一个基于 Vision Transformer（ViT）模型，部署于 RK3588（Orange Pi 5）嵌入式平台，并结合 PySide2 图形界面的果蔬自动识别结算系统，旨在应用于自助收银等智慧零售场景。

---

## 项目简介

本项目整合深度学习图像分类、嵌入式推理、串口通信、图形用户界面等多项技术，构建了一个具备完整功能的超市果蔬自动识别与结算系统：

- 使用 Vision Transformer（ViT）模型识别果蔬图像；
- 将模型部署至 RK3588 平台，并通过 RKNN Toolkit 加速推理；
- 由 STM32 控制的称重模块负责实时重量采集，确保计价准确；
- 前端界面使用 PySide2（Qt for Python）开发，支持触摸屏交互，界面美观易用；
- 系统支持商品自动识别、去皮、购物车管理、结算等功能，用户体验良好。

---

## 项目特点

- 🎯 **高精度识别**  
  利用 ViT 模型对多种果蔬种类进行图像分类，识别准确率达 96.94%。

- ⚙️ **嵌入式部署**  
  使用 RKNN-Toolkit2 将 PyTorch 模型转换为 RKNN 格式，部署在 RK3588 芯片（Orange Pi 5）上运行，充分利用其 6 TOPS NPU。

- ⚖️ **精准称重与计价**  
  STM32 通过 HX711 获取应变传感器数据，确保重量准确；结合识别结果进行自动计价。

- 🖥️ **图形用户界面（GUI）**  
  使用 PySide2 构建，支持触摸屏，交互友好；支持购物车功能、商品修改、结算、扫码/现金支付。

- 🔁 **实时处理，响应迅速**  
  多线程和多进程并行处理图像推理与界面交互，系统响应时间短，稳定性强。

---

## 技术栈

- 模型部分：Vision Transformer（ViT） + PyTorch + ONNX + RKNN Toolkit2
- 硬件平台：Orange Pi 5（RK3588 芯片）、STM32、HX711、电子秤、USB 摄像头、7 寸 HDMI 触摸屏
- 前端界面：PySide2 (Qt for Python)
- 通信方式：USB 摄像头 + 串口（UART）重量数据传输

---

## 项目目录结构

```plaintext
ViT-RK3588-PySide2-FruitCashier
├── model/              # ViT 模型文件（PyTorch / ONNX / RKNN）
├── app/                # PySide2 前端界面
├── app_lite/           # PySide2 前端界面精简版
├── LICENSE             # 项目许可证
└── README.md           # 项目说明（本文件）
```


---

## 依赖说明

- **硬件依赖**  
  - Orange Pi 5 (RK3588上)  
  - 摄像头（USB 接口，高拍仪或其他高清摄像头）  
  - STM32 + HX711 + 称重传感器  
  - 7 寸触摸屏 (HDMI 输出 + USB 触控)  

- **软件依赖**  
  - Python 3.8+  
  - PySide2 (Qt for Python)  
  - PyTorch（用于模型训练）  
  - RKNN-Toolkit2（模型转换及部署）  
  - 其他常用科学计算库 (numpy, opencv-python, etc.)

---
