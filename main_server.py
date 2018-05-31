import socket
import threading
import re
import dynamic.mini_web_frame


class Server(object):
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 8989))
        self.server_socket.listen(128)
        self.index = 0

    def __del__(self):
        self.server_socket.close()
        print('本次一共有%d个用户访问' % self.index)

    @staticmethod
    def show_menu():
        print('个人TCP服务器已运行')

    def run_forever(self):
        while True:
            client_socket, client_ip = self.server_socket.accept()
            print(client_ip, '用户访问服务器')
            self.index += 1
            # self.handle_request(client_socket)
            # 多线程
            th1 = threading.Thread(target=self.handle_request, args=(client_socket,))
            th1.setDaemon(1)
            th1.start()

    def set_response(self, status, headers):
        self.status = status
        self.headers = headers
        pass

    def handle_request(self, socket):
        content = socket.recv(4096).decode('utf-8')
        line_list = content.split('\r\n')
        first_line = line_list[0]
        if first_line:
            file_name = re.match(r'[^/]+(/[^ ]*)', first_line).group(1)
            if file_name == '/':
                file_name = '/index.html'
            if not file_name.endswith('dy.html'):
                # 静态页面
                try:
                    f = open('./static' + file_name, 'rb')

                except Exception as ret:
                    response_header = 'HTTP/1.1 400 not found\r\n'
                    response_body = str(ret).encode()
                    response_header += 'Server：YL_SERVER\r\n'
                    response_header += 'Content-Type: text/html; charset=utf-8\r\n\r\n'
                    socket.send(response_header.encode('utf-8') + response_body)
                else:
                    response_body = f.read()
                    f.close()
                    response_header = 'HTTP/1.1 200 OK\r\n'
                    response_header += 'Server：YL_SERVER\r\n\r\n'
                    # response_header += 'Upgrade-Insecure-Requests:1\r\n'
                    # response_header += 'Content-Type: text/html; charset=utf-8\r\n\r\n'
                    # socket.send(response_header.encode('utf-8') + response_body)
                    socket.send(response_header.encode())
                    socket.send(response_body)
                finally:
                    # response_header += 'Server：YL_SERVER\r\n'
                    # response_header += 'Content-Type: text/html; charset=utf-8\r\n\r\n'
                    # socket.send(response_header.encode('utf-8') + response_body)
                    socket.close()
            else:
                # 动态页面
                envor = dict()
                envor['url'] = file_name
                response_body = dynamic.mini_web_frame.application(envor, self.set_response)
                response_header = 'HTTP/1.1 %s' %self.status
                for i in self.headers:
                    response_header += '%s:%s\r\n'%(i[0], i[1])

                response_header += '\r\n'
                socket.send(response_header.encode() + response_body)
                pass


if __name__ == '__main__':
    YL = Server()
    YL.show_menu()
    YL.run_forever()
