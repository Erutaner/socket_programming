"""
Author: Erutaner
Date: 2022.12.28
"""
#  这个服务器会简单地将其收到的任何内容echo给客户端
# echo-server.py

import socket

HOST = "127.0.0.1"  # 标准环回接口地址（本地主机） 这玩意如果为空串
PORT = 65432  # 要侦听的端口 (非特权端口要 > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #创建一个socket对象 支持context manager type，所以能用with
# AF_INET表示IPV4, SOCK_STREAM表示socket type为TCP
    s.bind((HOST, PORT)) # 将s这个socket与对应的网络接口和端口号联系起来
    s.listen() # 使服务器变成一个listening socket，允许接受连接
    conn, addr = s.accept() #当有client连接的时候，返回一个新的表征连接的socket对象conn，和一个(host, port) tuple
# 这个accept会一直等，等到有接入为止
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024) #读取数据
            if not data: #如果传来空的字节对象 b''则证明客户已经关闭了连接
                break
            conn.sendall(data) # 将数据echo回去
