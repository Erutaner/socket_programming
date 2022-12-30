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
while True:  # 最外层循环用于登录
    user_name = input('Please input your user name:').strip()
    passwd = input("Please input your password:").strip()
    client.send(user_name.encode('utf-8'))  # 将输入的用户名编码后进行传输
    client.send(passwd.encode('utf-8'))  # 将输入的密码编码后传输
    res = client.recv(1020)   # 接收服务器对账号密码判定的结果
    print(res.decode('utf-8'))   # 解码后对本次登录结果输出
    if res.decode('utf-8') == "Log in successfully":  # 若登录有效，则进入
        while True:
            inp = input('>>>：').strip()
            # 向服务端发送数据，需要转换成Bytes类型发送
            client.send(inp.encode('utf-8'))
            if inp == 'bye':
                break  # 双层循环唯一出口
            # 接收服务端回应给客户端的数据，不能超过1024字节
            res = client.recv(1024)

            print(res.decode('utf-8'))
    else:
        continue
    print("Disconnected.")
    break


# 套接字关闭
client.close()
