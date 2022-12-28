"""
Author: Erutaner
Date: 2022.12.28
"""
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
#为了put the socket in non-blocking mode
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    # 这相当于创建了一个对象，里面就addr和inb outb这几个属性
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # READ是1  WRITE是10   则events应当是11
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        # 如果socket ready for reading，那这个就是True
        recv_data = sock.recv(1024)  # Should be ready to read，这里应当是从对面读过来
        if recv_data:
            data.outb += recv_data
            # 读到的数据都被加到这个outb里面
        else:  # 处理未接收到数据的情况（这意味着客户已经关闭了这个socket，则server也应当将之关闭）
            # 关之前需要先调用unregister，这样就不再被.select监控了
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write，从发送缓冲区里发
            # 把接收到的数据echo回client那边去 send方法返回发送的字节数
            data.outb = data.outb[sent:] # 已经从缓冲区发出去的部分应当被去掉


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 这个socket是服务器用来listen的
# lsock全称：listening socket
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False) # 将socket配置为non-blocking mode
# 可以等待一个或多个socket的event
sel.register(lsock, selectors.EVENT_READ, data=None)
# 因为lsock是个listening socket，所以第二个参数为READ，做完这个操作后the listening socket should be ready to read


try:
    while True:
        events = sel.select(timeout=None)
# blocks until there are sockets ready for I/O
# select返回一个由元组构成的列表 元组：(key, mask) key.fileobj是一个socket object
# mask是个event mask表征操作已经准备好了
# key.data用来追踪这个socket发送或收到了什么，如果是none则来自listening socket，则你需要接受connection
# 应该说listenning socket都需要用selector来register一下
# key.data不是none，则是个client socket，而且已经被accepted了，下面需要提供服务
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()