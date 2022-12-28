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
    data = s.recv(1024)  # 读取服务器的回应
# 将之打印
print(f"Received {data!r}")
