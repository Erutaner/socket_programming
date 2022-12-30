"""
Author: Erutaner
Date: 2022.12.30
"""
import pymysql
import socket
from my_arg import MY_SERVER_IP, MY_SERVER_PORT

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

# 创建套接字对象，AF_INET基于IPV4通信，SOCK_STREAM以数据流的形式传输数据，这里就可以确定是TCP了
server = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)

# server = socket.socket() 等同于上面的写法

# 绑定ip地址和端口，127.0.0.1代表回环地址，只能当前计算机访问
server.bind((MY_SERVER_IP,MY_SERVER_PORT))

# 建立半链接池，允许存放5个请求
server.listen(5)

# 等待建立连接请求，会返回两个值，一个是连接状态，一个是连接的客户端IP与端口
print("The server is waiting for connection...")
conn,ip_addr = server.accept()

while True:  # 最外层循环用于登录
    # 接收客户端传递的数据，只接收1024个字节数据
    user_name = conn.recv(1024)
    passwd = conn.recv(1024)
    ret = log_in_test(user_name.decode('utf-8'),passwd.decode('utf-8'))
    conn.send(ret.encode('utf-8'))
    if ret == "Log in successfully":
        print(f"Connection form {ip_addr}")
        while True:
            # 接收客户端传递的数据，只接收1024个字节数据
            res = conn.recv(1024)
            if res.decode("utf-8") == 'bye':
                break
            # 将客户端的数据接收到以后，转换成大写再编码后发送给客户端
            conn.send(res.decode('utf-8').upper().encode('utf-8'))
    else:
        continue
    print("Disconnected.")
    break



# 关闭与客户端的连接
conn.close()

# 关闭套接字
server.close()

