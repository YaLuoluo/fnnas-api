from .encryption import aes_decrypt


async def HandlerDefault(client, data):
    if "errno" in data:
        error_code = data["errno"]
    # 测试抛出错误， 程序会不会停止 如果except Exception就不会，不except Exception就会停止


async def HandlerGetRSAPub(client, data):
    client.pub = data.get('pub', None)
    client.si = data.get('si', None)


async def HandlerLogin(client, data):
    # 以下是登录返回
    client.backId = data.get('backId', None)
    client.token = data.get('token', None)
    client.secret = data.get('secret', None)
    client.uid = data.get('uid', None)
    client.admin = data.get('admin', None)
    client.sign_key = aes_decrypt(client.secret, client.key, client.iv)
