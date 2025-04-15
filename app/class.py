class MyClass:
    def instance_method(self):
        print("调用实例方法，访问实例：", self)

    @classmethod
    def class_method(cls):
        print("调用类方法，访问类：", cls)

    @staticmethod
    def static_method():
        print("调用静态方法，不自动传递self或cls")

def global_function():
    print("这是一个全局函数")

# 创建实例
obj = MyClass()

# 调用实例方法
obj.instance_method()  # 输出：调用实例方法，访问实例： <MyClass instance>

# 调用类方法
MyClass.class_method()  # 输出：调用类方法，访问类： <class 'MyClass'>

# 调用静态方法
MyClass.static_method()  # 输出：调用静态方法，不自动传递self或cls
obj.static_method()

# 调用全局函数
global_function()  # 输出：这是一个全局函数
