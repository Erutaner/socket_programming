"""
Author: Erutaner
Date: 2022.12.30
"""
import pymysql
import socket
from my_arg import MY_SERVER_IP, MY_SERVER_PORT
from _thread import *
import struct
import json
from my_func import *

ThreadCount = 0


def echo_str_back(conn):
    while True:  # 以下是信息传输过程，与前一个版本一致
        # 接收客户端传递的数据，只接收1024个字节数据
        header_received = conn.recv(4)  # 由于那个header就4字节，所以接收header也用4字节
        data_len = struct.unpack('i',header_received)[0]  # 这一坨返回的是发送过来数据的长度
        count = 0  # 设置个小计数器
        res = b""
        while count < data_len:
            res += conn.recv(3)
            count = len(res)

        if res.decode("utf-8") == 'bye':
            return
        # 将客户端的数据接收到以后，转换成大写再编码后发送给客户端
        header_sent = struct.pack('i',len(res))  # 服务器端要发送的数据设置首部
        conn.sendall(header_sent)  # 把这个首部发送过去
        conn.sendall(res.decode('utf-8').upper().encode('utf-8'))


def server_file_trans(conn):
    while True:
        client_choice = conn.recv(1024).decode('utf-8')
        if client_choice == 'u':
            server_file_receiving(conn)
        elif client_choice == 'd':
            server_file_sending(conn)
        elif client_choice == 'bye':
            return
        else:
            continue




def log_in_test(user_name,passwd):
    # 创建连接对象
    sql_conn = pymysql.connect(host='localhost',port=3306,user='root',password='zj20030811'\
                               ,database='client_info',charset='utf8')
    # 获取游标对象
    cursor = sql_conn.cursor()
    # 写个语句
    user_sql = f"select * from info where user_name = '{user_name}';"
    cursor.execute(user_sql)
    sel_result = cursor.fetchone()
    # print(f"the result is {sel_result}")  这行只是为了输出数据库中的命中记录，在实际运行中没必要
    if sel_result is not None:
        if sel_result[1] == passwd:
            ret = "Log in successfully"
        else:
            ret = 'Access denied.'
    else:
        ret = "Account doesn't exist."
    cursor.close()
    sql_conn.close()
    return ret


def newly_sign_up(user_name,passwd):
    # 创建连接对象
    sql_conn = pymysql.connect(host='localhost', port=3306, user='root', password='zj20030811' \
                               , database='client_info', charset='utf8')
    # 获取游标对象
    cursor = sql_conn.cursor()
    # 我再写个语句
    user_sql = f"insert into info values('{user_name}','{passwd}');"
    # 执行以下这个语句，注意处理错误
    try:
        cursor.execute(user_sql)
        # 提交数据到数据库
        sql_conn.commit()
        ret = "Account created."
    except Exception as e:
        sql_conn.rollback()
        ret = "Account has already existed."
    finally:
        # 关闭游标
        cursor.close()
        # 关闭连接
        sql_conn.close()
        return ret


def read_conn(conn):
    for tup in conn_ls:
        if tup[0] == conn:
            return tup[1]


def multi_threaded_client(conn):
    ip_addr = read_conn(conn)
    while True:  # 最外层循环用于登录
        # 接收客户端传递的数据，只接收1024个字节数据
        user_name = conn.recv(1024)  # 接收客户端输入的用户名
        if user_name.decode('utf-8') == "sign up":
            while True:  # 循环注册
                user_name = conn.recv(1024)
                passwd = conn.recv(1024)
                # 将注册信息写入数据库，若写入出现了问题还得让客户再换个用户名
                sign_up_ret = newly_sign_up(user_name.decode('utf-8'), passwd.decode('utf-8'))
                conn.send(sign_up_ret.encode('utf-8'))
                if sign_up_ret == "Account has already existed.":
                    continue
                else:
                    # 将这个用户名和密码写入数据库后，不用再验证合法性，返回信息后直接登入
                    ret = "Log in successfully"
                    conn.send(ret.encode('utf-8'))  # 将合法性返回给客户，便于其知晓自己的登入状态
                    if ret == "Log in successfully":  # 只有登入合法，才能继续进行信息接收操作
                        print(f"Connection from {ip_addr}")  # 一个在server本端现实的连接信息
                        # echo_str_back(conn)  # 利用这个函数跟客户交互信息
                        server_file_trans(conn)
                    else:
                        continue
                    print(f"{ip_addr} disconnected.")
                    break
        else:
            user_name = conn.recv(1024)
            passwd = conn.recv(1024)  # 接收客户端输入的密码

            ret = log_in_test(user_name.decode('utf-8'), passwd.decode('utf-8'))  # 用函数验证合法性
            conn.send(ret.encode('utf-8'))  # 将合法性返回给客户，便于其知晓自己的登入状态
            if ret == "Log in successfully":  # 只有登入合法，才能继续进行信息接收操作
                print(f"Connection from {ip_addr}")  # 一个在server本端现实的连接信息
                # echo_str_back(conn)
                server_file_trans(conn)
            else:
                continue
            print(f"{ip_addr} disconnected.")
            break
        break
    # 关闭与客户端的连接
    conn.close()




# 创建套接字对象，AF_INET基于IPV4通信，SOCK_STREAM以数据流的形式传输数据，这里就可以确定是TCP了
server = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)

# server = socket.socket() 等同于上面的写法

# 绑定ip地址和端口，127.0.0.1代表回环地址，只能当前计算机访问
server.bind((MY_SERVER_IP,MY_SERVER_PORT))

# 建立半链接池，允许存放5个请求
server.listen(5)

# 等待建立连接请求，会返回两个值，一个是连接状态，一个是连接的客户端IP与端口
print("The server is waiting for connection...")
conn_ls = []  # 我们借助这个列表来判定某个线程中处理的是哪一个port
while True:
    conn,ip_addr = server.accept()
    conn_ls.append((conn,ip_addr))

    start_new_thread(multi_threaded_client,(conn, ))
    ThreadCount += 1
    print("Current Thread Number: " + str(ThreadCount))


# 关闭套接字
server.close()

