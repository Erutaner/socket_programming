"""
Author: Erutaner
Date: 2022.12.28
"""
# echo-client.py

import socket

HOST = "127.0.0.1"  # 服务器主机名或IP地址
PORT = 65432  # 服务器使用的端口

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # 创建socket对象
    s.connect((HOST, PORT))  # 连接服务器
    s.sendall(b"Hello, world")  # 发送消息
    data = s.recv(1024)  # 读取服务器的回应，1024的是bufsize，是一次最多接收的数据，但并不意味着recv一次就返回1024bytes
# 资料说应用程序负责检查是不是所有数据都已被发送，如果只有部分被发送，那得想办法再把剩下的发出去
# sendall这个方法要么一口气发送完数据，要么就是传输过程中出错了，若传输成功则返回None，可以避免上述问题
# 若用的是send和recv(上面有recv这个方法而没有其他操作，所以应该是有隐患的)，就得额外保证所有的数据都被发送或者被接受
# 将之打印
print(f"Received {data!r}")
