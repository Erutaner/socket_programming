"""
Author: Erutaner
Date: 2022.12.31
"""
import json
import struct

def client_file_sending(client):
    file_name = input("Please input the name of your file:").strip()
    # file_type = re.findall(r'.[^./:*?"<>|]+$', file_name)[0]  # 使用正则表达式提取文件后缀
    file_path = ".\\client_file\\" + file_name
    file_open_check = "unchecked"
    try:
        # 把待发送文件以二进制度方式打开
        file_to_send = open(file_path, "rb")
        # 成功打开文件后发送确认信息
        file_open_check = "checked"
        client.sendall(file_open_check.encode('utf-8'))
        # 读取文件中的内容
        file_data = file_to_send.read()
        # 自定义文件首部
        file_header = {"file_size": len(file_data), "file_name": file_name}
        # 将之序列化并转化为二进制
        file_header_bytes = bytes(json.dumps(file_header), encoding='utf-8')
        # 将这个首部打包并发送打包消息
        header_bytes_len = struct.pack('i', len(file_header_bytes))
        client.sendall(header_bytes_len)
        # 将首部发送
        client.sendall(file_header_bytes)
        # 将数据发送
        client.sendall(file_data)
        print(f"{file_name} has been sent.")
        file_to_send.close()
    except Exception as e:
        print(e)
        client.sendall(file_open_check.encode('utf-8'))
    finally:
        return



def client_file_receiving(client):
    file_download_name = input("Please input the name of your file to download:").strip()
    client.sendall(file_download_name.encode('utf-8'))
    check_file = client.recv(1024).decode('utf-8')
    if check_file == "File is found.":
        # 接收数据首部的首部的信息
        header_len_bytes = client.recv(4)
        # 取出首部长度
        header_len = struct.unpack('i', header_len_bytes)[0]
        # 根据这个长度接收首部
        header_bytes = client.recv(header_len)
        # 将首部解码出来
        header = json.loads(header_bytes.decode('utf-8'))
        # 取出首部中的信息
        file_received_name = header["file_name"]
        file_received_size = header['file_size']
        count = 0
        file_data = b""
        while count < file_received_size:
            file_data += client.recv(1020)
            count = len(file_data)
        print(f"File {file_received_name}: excepted {file_received_size} bytes, received {count} bytes.")
        if file_received_size == count:
            print("Received successfully.")
        try:
            new_file = open(".\\client_file\\" + file_received_name, 'wb')
            new_file.write(file_data)
        except Exception as e:
            print(e)
        finally:
            new_file.close()
    else:
        print(check_file)
        return


def server_file_sending(conn):
    file_name = conn.recv(1024).decode('utf-8')
    # file_type = re.findall(r'.[^./:*?"<>|]+$', file_name)[0]  # 使用正则表达式提取文件后缀
    file_path = ".\\server_file\\" + file_name
    try:
        # 把待发送文件以二进制方式打开
        file_to_send = open(file_path, "rb")
        conn.sendall("File is found.".encode('utf-8'))
        # 读取文件中的内容
        file_data = file_to_send.read()
        # 自定义文件首部
        file_header = {"file_size": len(file_data), "file_name": file_name}
        # 将之序列化并转化为二进制
        file_header_bytes = bytes(json.dumps(file_header), encoding='utf-8')
        # 将这个首部打包并发送打包消息
        header_bytes_len = struct.pack('i', len(file_header_bytes))
        conn.sendall(header_bytes_len)
        # 将首部发送
        conn.sendall(file_header_bytes)
        # 将数据发送
        conn.sendall(file_data)
        print(f"{file_name} has been sent.")

    except Exception as e:
        conn.sendall(str(e).encode('utf-8'))
    finally:
        return

def server_file_receiving(conn):
    file_open_check = conn.recv(1024).decode('utf-8')
    if file_open_check == "unchecked":
        return
    else:
        # 接收数据首部的首部的信息
        header_len_bytes = conn.recv(4)
        # 取出首部长度
        header_len = struct.unpack('i', header_len_bytes)[0]
        # 根据这个长度接收首部
        header_bytes = conn.recv(header_len)
        # 将首部解码出来
        header = json.loads(header_bytes.decode('utf-8'))
        # 取出首部中的信息
        file_received_name = header["file_name"]
        file_received_size = header['file_size']
        count = 0
        file_data = b""
        while count < file_received_size:
            file_data += conn.recv(1020)
            count = len(file_data)
        print(f"File {file_received_name}: excepted {file_received_size} bytes, received {count} bytes.")
        if file_received_size == count:
            print("Received successfully.")
        try:
            new_file = open(".\\server_file\\" + file_received_name, 'wb')
            new_file.write(file_data)
        except Exception as e:
            print(e)
        finally:
            new_file.close()

