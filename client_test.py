"""
Author: Erutaner
Date: 2022.12.30
"""
import socket
from my_arg import MY_SERVER_PORT, MY_SERVER_IP
import struct

def loop_str_sending(client):
    while True:
        inp = input('>>>：').strip()
        # 将这个数据的长度转换为一个四字节的类型，存入header_sent
        header_sent = struct.pack("i",len(inp.encode('utf-8')))
        client.sendall(header_sent)   # 把这玩意作为数据首部发出去
        # 向服务端发送数据，需要转换成Bytes类型发送
        client.sendall(inp.encode('utf-8'))
        if inp == 'bye':
            return  # 双层循环唯一出口
        header_received = client.recv(4)  # 接收首部
        data_len = struct.unpack('i', header_received)[0]  # 这一坨返回的是发送过来数据的长度
        res = b""  # 这个用来接收数据
        count = 0  # 设置一个小计数器
        while count < data_len:
            res += client.recv(3)
            count = len(res)

        print(res.decode('utf-8'))



# 创建套接字对象，AF_INET基于IPV4通信，SOCK_STREAM以数据流的形式传输数据，这里就可以确定是TCP了
client = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)

# 连接服务端
client.connect((MY_SERVER_IP,MY_SERVER_PORT))
while True:  # 最外层循环用于登录
    user_name = input('Please input your user name, if you don\'t have one, input sign up to sign up:').strip()
    client.send(user_name.encode('utf-8'))

    # 注册模块
    if user_name == "sign up":
        while True:
            user_name = input("Please set your user name:").strip()
            passwd = input("Please set your password, after then you can sign in:").strip()
            client.send(user_name.encode('utf-8'))  # 将输入的用户名编码后进行传输
            client.send(passwd.encode('utf-8'))  # 将输入的密码编码后传输
            sign_up_ret = client.recv(1020)
            print(sign_up_ret.decode('utf-8'))
            if sign_up_ret.decode('utf-8') == "Account has already existed.":
                continue
            else:
                res = client.recv(1020)  # 接收服务器对账号密码判定的结果
                print(res.decode('utf-8'))  # 解码后对本次登录结果输出
                if res.decode('utf-8') == "Log in successfully":  # 若登录有效，则进入, 这里一定有效，其实没必要了
                    loop_str_sending(client)
                else:
                    continue
                print("Disconnected.")
                break


    # 登录模块
    else:
        passwd = input("Please input your password:").strip()
        client.send(user_name.encode('utf-8'))  # 将输入的用户名编码后进行传输
        client.send(passwd.encode('utf-8'))  # 将输入的密码编码后传输
        res = client.recv(1020)   # 接收服务器对账号密码判定的结果
        print(res.decode('utf-8'))   # 解码后对本次登录结果输出
        if res.decode('utf-8') == "Log in successfully":  # 若登录有效，则进入
            loop_str_sending(client)
        else:
            continue
        print("Disconnected.")
        break
    break
# 套接字关闭
client.close()
