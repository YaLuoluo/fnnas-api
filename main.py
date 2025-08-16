import asyncio
from sdk import FnOsClient
from sdk.handlers import HandlerUserInfo


async def main():
    # 启动飞牛连接
    client = FnOsClient(ping_interval=60)
    await client.connect('ws://117.154.73.48:9722/websocket?type=main')
    client.add_handler('user.info', HandlerUserInfo)

    try:
        login_res = await client.login('HKB', 'BJGX0726@')
        print("login_res", login_res)
        res = await client.user_info()
        print("user_info", res)
        res = await client.authToken() # 非必须
        print("authToken", res)
        
        # 上传文件 上传时修改sdk中的链接地址  懒得写配置项了
        local_path = r'success.txt'
        nas_path = f'/vol2/1000/Temp/success.txt' # NAS绝对路径
        res = await client.upload(local_path, nas_path)
        print("upload res", res)

        # 修改端口
        res = await client.setting_port(
            http_port=5666,    # 自定义HTTP端口
            https_port=5668,   # 自定义HTTPS端口
            force_https=False, # 不强制HTTPS
            redirect=True      # 开启端口跳转
        )
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
