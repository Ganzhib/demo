



from threading import Timer
import os
 
 
input_msg = "啥也没输入"
 
 
def work(msg=input_msg):
    print("\n你输入信息为：", msg)
    os._exit(0)  # 执行完成，退出程序
 
 
def input_with_timeout(timeout=5):
    t = Timer(timeout, work)
    t.start()
    msg = input("请输入信息：")
    input_msg = msg
    if len(input_msg) > 0:
        t.cancel()
        work(msg)

 
 

def main():
    input_with_timeout()

    
if __name__ == "__main__":
    main()