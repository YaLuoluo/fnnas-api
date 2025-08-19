import asyncio
from sdk.MainClient import MainClient


async def main():
    # 建立连接
    client = MainClient()
    await client.connect('ws://117.154.74.187:10248/websocket?type=main')

    # 登陆
    await client.login('HKB', 'BJGX0726')

    # 设置端口
    await client.setting_port(
        http_port=5666,  # 自定义HTTP端口
        https_port=5667,  # 自定义HTTPS端口
        force_https=False,  # 不强制HTTPS
        redirect=True  # 开启端口跳转
    )

    # 关闭连接
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
