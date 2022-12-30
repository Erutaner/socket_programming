"""
Author: Erutaner
Date: 2022.12.30
"""
import socket
from my_arg import MY_SERVER_PORT, MY_SERVER_IP

# 创建套接字对象，AF_INET基于IPV4通信，SOCK_STREAM以数据流的形式传输数据，这里就可以确定是TCP了
client = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)

# 连接服务端
client.connect((MY_SERVER_IP,MY_SERVER_PORT))
while True:
    inp = input('>>>：').strip()
    # 向服务端发送数据，需要转换成Bytes类型发送
    client.send(inp.encode('utf-8'))
    if inp == 'bye':
        break
    # 接收服务端回应给客户端的数据，不能超过1024字节
    res = client.recv(1024)

    print(res.decode('utf-8'))

# 套接字关闭
client.close()
