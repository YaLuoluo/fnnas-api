import json
import os
from abc import ABC

from sdk.encryption import login_encrypt, get_signature_req
from sdk.handlers import HandlerDefault, HandlerLogin, HandlerGetRSAPub
from sdk.utils import generate_random_string, get_reqid
import websockets
import asyncio


class BaseClient(ABC):
    def __init__(self):
        self.websocket = None
        self.handlers = {}
        self.pending_requests = {}
        self.req_mapping = {}

        self._listen_task = None
        self.__url = None

        # 下面数据自动初始化
        self.sign_key = None
        self.key = generate_random_string(32)
        self.iv = os.urandom(16)

        # 网站数据, 不用赋值，自动赋值
        self.si = None
        self.pub = None
        # 以下登录返回
        self.backId = '0000000000000000'
        self.token = None
        self.secret = None
        self.uid = None
        self.admin = None

    async def _init(self):
        # 这里注册回调函数，如果要给MainClient加处理请求，在这里加
        self.add_handler('util.crypto.getRSAPub', HandlerGetRSAPub)
        self.add_handler('user.login', HandlerLogin)
        # 连接后执行的方法
        await self.request(req='util.crypto.getRSAPub')

    async def _listen(self):
        print("-----开始监听-----：")
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                print("收到数据：", message)
                if 'reqid' in data:
                    reqid = data['reqid']
                    # 返回响应
                    if reqid in self.pending_requests:
                        handler = self.pending_requests.pop(reqid)
                        handler(data)
                    # TODO：尝试使用默认处理器抛出错误
                    # 检查错误放在这里，放在前面request一直卡
                    # check_response(data)
                    # 处理响应
                    if reqid in self.req_mapping:
                        req_type = self.req_mapping.pop(reqid)
                        handler = self.handlers.get(req_type, HandlerDefault)
                        await handler(self, data)
                else:
                    # 处理没有reqid的消息
                    print("未知数据：", data)
            except asyncio.CancelledError:
                print("监听退出")
                break
            except websockets.ConnectionClosed as e:
                print("Websocket连接关闭")
                break
            # 如果不except Exception程序会停止吗？？  会 但是主进程不会抛出错误 卡死
            except Exception as e:
                print("发生错误：", e)
        print("-----监听停止-----")

    async def connect(self, url: str = None):
        self.__url = url
        try:
            # 坑 服务器不会响应ping，他是使用消息进行ping测活， 所以关闭框架的自动ping
            self.websocket = await websockets.connect(self.__url, ping_interval=None)

            # 创建监听任务
            self._listen_task = asyncio.create_task(self._listen())

            # 初始化， 继承的类实现
            await self._init()
        except websockets.WebSocketException as e:
            print("连接错误")

    def add_handler(self, req, handler):
        self.handlers[req] = handler

    async def request(self, req, **kwargs):
        reqid = await self.send_request(req, **kwargs)
        future = asyncio.Future()
        self.pending_requests[reqid] = lambda data: future.set_result(data)
        return await future

    async def send_request(self, req, **kwargs):
        reqid = get_reqid(self.backId)
        data = {'req': req, 'reqid': reqid, **kwargs}
        if req == 'user.login':
            # 加密
            data = json.dumps(data, separators=(',', ':'))
            data = login_encrypt(data, self.pub, self.key, self.iv)

        # 签名
        message = get_signature_req(data, self.sign_key)

        await self.websocket.send(message)
        self.req_mapping[reqid] = req
        print("发送数据：", req + "：" + message)
        return reqid


class MainClient(BaseClient):

    async def login(self, username, password, *, deviceType='Browser', deviceName='HookProgram-PortUpdate', stay=False):
        data = {
            "user": username,
            "password": password,
            "deviceType": deviceType,
            "deviceName": deviceName,
            "stay": stay,
            "si": self.si
        }
        response = await self.request('user.login', **data)
        return response

    async def setting_port(self, force_https=False, redirect=True, http_port=5666, https_port=5667):
        data = {
            "data": {
                "force_https": force_https,  # 强制Https
                "redirect": redirect,  # 是否重定向，80和443跳转
                "schema": {
                    "http": {
                        "port": http_port  # HTTP端口
                    },
                    "https": {
                        "port": https_port  # HTTPS端口
                    }
                }
            }
        }
        response = await self.request('appcgi.network.gw.setting', **data)
        return response

    async def close(self):
        """关闭连接并取消所有任务"""
        if self._listen_task:
            self._listen_task.cancel()

        print("释放监听")
