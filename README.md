目前已经实现ws断开自动重连（会重新登录）

快速入门：
```python
import asyncio
from sdk import FnOsClient
from sdk.handlers import HandlerUserInfo


async def main():
    # 启动飞牛连接
    client = FnOsClient(ping_interval=60)
    await client.connect('ws://172.24.120.213:5666/websocket?type=main')
    client.add_handler('user.info', HandlerUserInfo)

    try:
        login_res = await client.login('dev', '8GMu~_u+nD1Rj3')
        print("login_res", login_res)
        res = await client.user_info()
        print("user_info", res)
        res = await client.authToken() # 非必须
        print("authToken", res)
        
        # 上传文件 上传时修改sdk中的链接地址  懒得写配置项了
        local_path = r'C:\Users\Administrator\Pictures\bg.jpg'
        nas_path = f'vol1/1001/tmp_img/bg.jpg' # NAS绝对路径
        res = await client.upload(local_path, nas_path)
        print("upload res", res)

        # 修改端口
        res = await client.setting_port()
        print("setting_port", res)

        # 永久运行（直到手动停止）
        await asyncio.Event().wait()

        # 运行60s停止
        # await asyncio.sleep(60)
        # await client.close()
    except KeyboardInterrupt:
        print('中断进程')
        print('关闭client')
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

SDK没有优化，很多异常没有处理，只是能用，不好用。大佬们封装吧

#### TODO

 - [x] 登录
 - [x] 验证Token
 - [x] 心跳
 - [x] 用户详细信息
 - [x] 文件列表
 - [x] 文件上传
 - [x] 端口修改
 - [ ] 文件下载
 - [ ] 文件双向同步 [我改了SMB方案，所以可能不更新了]
 - [ ] 其他接口
