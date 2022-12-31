"""
Author: Erutaner
Date: 2022.12.30
"""
import socket
from my_arg import MY_SERVER_PORT, MY_SERVER_IP
import struct
import re
import json

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


def client_file_trans(client):
    # 应当能实现手动输入路径与文件名后取文件
    file_name = input("Please input the name of your file:").strip()
    # file_type = re.findall(r'.[^./:*?"<>|]+$', file_name)[0]  # 使用正则表达式提取文件后缀
    file_path = ".\\client_file\\" + file_name
    try:
        # 把待发送文件以二进制度方式打开
        file_to_send = open(file_path,"rb")
        # 读取文件中的内容
        file_data = file_to_send.read()
        # 自定义文件首部
        file_header = {"file_size":len(file_data),"file_name":file_name}
        # 将之序列化并转化为二进制
        file_header_bytes = bytes(json.dumps(file_header),encoding = 'utf-8')
        # 将这个首部打包并发送打包消息
        header_bytes_len = struct.pack('i',len(file_header_bytes))
        client.sendall(header_bytes_len)
        # 将首部发送
        client.sendall(file_header_bytes)
        # 将数据发送
        client.sendall(file_data)
        print(f"{file_name} has been sent.")

    except Exception as e:
        print(e)
    finally:
        file_to_send.close()
        return

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
                    # loop_str_sending(client)
                    client_file_trans(client)
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
            # loop_str_sending(client)
            client_file_trans(client)
        else:
            continue
        print("Disconnected.")
        break
    break
# 套接字关闭
client.close()
