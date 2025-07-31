# -*- coding:utf-8 -*-

import json
import traceback
import os
import shutil
import tempfile
import os.path as osp
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from main import Data_Spider


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def _send_response(self,
                       status_code,
                       content_type,
                       body=None,
                       fileobj=None):
        '''发送响应信息'''
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Cache-Control', 'no-store')  # 防止缓存旧编码响应
        if body:
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        if fileobj:
            size = fileobj.seek(0, os.SEEK_END)
            fileobj.seek(0)
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition",
                             'attachment; filename=xhs-notes.zip')
            self.end_headers()
            shutil.copyfileobj(fileobj, self.wfile)
            fileobj.close()

    def _handle_home(self):
        '''访问主页请求处理'''

        html = open('./static/spider-xhs.html', 'r').read()
        self._send_response(200, 'text/html; charset=utf-8', html)

    def _handle_404(self):
        '''请求不存在资源处理'''

        # json_respose = {"success": False, "message": "Not Found"}
        # self._send_response(404, 'application/json;charset=utf-8', json.dumps(json_respose))

        # Content-Type 指定 charset=utf-8 可避免浏览器GET请求，界面中文显示乱码问题
        self._send_response(404, 'text/html; charset=utf-8',
                            "<h1>404 Not Found</h1>")

    def _handle_spider_xhs(self, req_data):
        '''处理登录请求'''

        try:
            data = json.loads(req_data)
            xhs_cookies = data.get('cookies', None)
            xhs_notes_url = data.get('notes_url', None)
            data_spider = Data_Spider()
            notes = xhs_notes_url.split(',')

            with tempfile.TemporaryDirectory() as tmpdirname:
                base_path = {
                    'media': tmpdirname,
                }
                data_spider.spider_some_note(notes, xhs_cookies, base_path,
                                             'media')

                temp_dir = tempfile.gettempdir()
                archive_fd, archive_path = tempfile.mkstemp(suffix='.zip',
                                                            dir=temp_dir)
                archive_path_b, _ = osp.splitext(archive_path)
                zf = shutil.make_archive(archive_path_b, 'zip', tmpdirname)
                self._send_response(200, 'application/octet-stream', None,
                                    open(archive_path, 'rb'))

        except Exception as e:
            error_msg = traceback.format_exc()
            print(error_msg)
            response = {'code': 1, 'token': '', 'description': error_msg}
            self._send_response(500, 'application/json; charset=utf-8',
                                json.dumps(response))

    def do_GET(self):
        '''处理GET请求'''

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)  # 获取URL携带的查询参数
        # print('收到GET请求参数:', query_params)

        if path == '/':
            self._handle_home()
        else:
            self._handle_404()

    def do_POST(self):
        '''处理POST请求'''

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)  # 获取URL 查询参数
        # print("收到POST数据:", post_data.decode())

        # 路由匹配逻辑
        if path == '/':
            self._handle_home()
        elif path == '/spider-xhs':
            self._handle_spider_xhs(post_data.decode())
        else:
            self._handle_404()


if __name__ == '__main__':
    # server = HTTPServer(('0.0.0.0', 8000), MyHandler) # 阻塞式运行
    server = ThreadingHTTPServer(('0.0.0.0', 8000), MyHTTPRequestHandler)
    print('正在启动服务，访问地址：http://localhost:8000')
    server.serve_forever()
