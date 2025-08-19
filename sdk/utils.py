import time
import random


def _get_reqid():
    index = 1
    def func(backId):
        nonlocal index
        t = format(int(time.time()), 'x').zfill(8)
        e = format(index, 'x').zfill(4)
        index += 1
        return f"{t}{backId}{e}"
    return func
get_reqid = _get_reqid()


# 生成随机字符串
def generate_random_string(t):
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(chars) for _ in range(t))
