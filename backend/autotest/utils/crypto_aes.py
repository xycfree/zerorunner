#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2022/11/29 16:53  @Author: wangbing3  @Descript:

"""
AES加密解密工具类
此工具类加密解密结果与 http://tool.chacuo.net/cryptaes 结果一致
数据块128位
key 为16位
iv 为16位，且与key相等
字符集utf-8
输出为base64
AES加密模式 为cbc
填充 pkcs7padding
"""

import base64
import random
from binascii import b2a_hex, a2b_hex

# pip install pycryptodomex
from Cryptodome.Cipher import AES
from config import config

def pkcs7_padding(text):
    """ 明文使用PKCS7填充
    最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
    :param text: 待加密内容(明文)
    :return:
    """
    bs = AES.block_size  # 16
    length = len(text)
    bytes_length = len(bytes(text, encoding='utf-8'))
    # tips：utf-8编码时，英文占1个byte，而中文占3个byte
    padding_size = length if (bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
    padding_text = chr(padding) * padding
    return text + padding_text


def pkcs7_unpadding(text):
    """
    处理使用PKCS7填充过的数据
    :param text: 解密后的字符串
    :return:
    """
    length = len(text)
    unpadding = ord(text[length - 1])
    return text[0:length - unpadding]


def encrypt(content: str, key: str = "", iv: str = "") -> str:
    """ AES加密
    key,iv使用同一个
    模式cbc
    填充pkcs7
    :param iv: iv
    :param key: 密钥
    :param content: 加密内容
    :return:
    """
    key = key if key else config.AES_KEY
    iv = iv if iv else config.AES_IV

    key_bytes = bytes(key, encoding='utf-8')
    iv_bytes = bytes(iv, encoding='utf-8')

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)  # 创建aes密码
    # 处理明文
    content_padding = pkcs7_padding(content)
    # 加密
    encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))

    # 重新编码 base64编码
    result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')  # base64加密

    # 重新编码 b2a_hex编码
    # result = b2a_hex(encrypt_bytes).decode('utf-8')  # b2a_hex加密 二进制数据的十六进制表示。

    return result


def decrypt(content: str, key: str = "", iv: str = "") -> str:
    """ AES解密
     key,iv使用同一个
    模式cbc
    去填充pkcs7
    :param iv:
    :param key:
    :param content:
    :return:
    """
    key = key if key else config.AES_KEY
    iv = iv if iv else config.AES_IV

    key_bytes = bytes(key, encoding='utf-8')
    iv_bytes = bytes(iv, encoding='utf-8')
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)

    # a2b_hex解码
    # plain_text = cipher.decrypt(a2b_hex(content))  # 十六进制转二进制进行表示

    # base64解密
    plain_text = cipher.decrypt(base64.b64decode(content))

    # 重新编码
    result = str(plain_text, encoding='utf-8')

    # 去除填充内容
    result = pkcs7_unpadding(result)
    return result


def get_key(c_length: int):
    """ 获取密钥 c_length 密钥长度
    :return:
    """
    source = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    length = len(source) - 1
    result = ''
    for i in range(c_length):
        result += source[random.randint(0, length)]
    return result


if __name__ == '__main__':
    # Test
    source_en = '12345678AK360!@#你好我是王春冬'
    print(f"原文: {source_en}")
    encrypt_en = encrypt(source_en)
    print(f"加密后内容：{encrypt_en}")
    # 解密
    decrypt_en = decrypt(encrypt_en)
    print(f"解密后内容: {decrypt_en}")
    print(source_en == decrypt_en)

    # 非16字节的情况
    # aes_key = get_key(16)
    # aes_key = "a36a1b37f64873b4541d36e59c77142b"
    # print('aes_key:' + aes_key)
    # 对英文加密
    # source_en = '12345678'
    # print(f"原文: {source_en}")
    # encrypt_en = encrypt(aes_key, source_en)
    # print(f"加密后内容：{encrypt_en}")
    # # 解密
    # decrypt_en = decrypt(aes_key, encrypt_en)
    # print(f"解密后内容: {decrypt_en}")
    # print(source_en == decrypt_en)

    # 中英文混合加密
    # source_mixed = 'Hello, 韩- 梅 -梅'
    # encrypt_mixed = encrypt(aes_key, source_mixed)
    # print(encrypt_mixed)
    # decrypt_mixed = decrypt(aes_key, encrypt_mixed)
    # print(decrypt_mixed)
    # print(decrypt_mixed == source_mixed)

    # 刚好16字节的情况
    # en_16 = 'abcdefgj10124567'
    # encrypt_en = encrypt(aes_key, en_16)
    # print(encrypt_en)
    # # 解密
    # decrypt_en = decrypt(aes_key, encrypt_en)
    # print(decrypt_en)
    # print(en_16 == decrypt_en)
    # mix_16 = 'abx张三丰12sa'
    # encrypt_mixed = encrypt(aes_key, mix_16)
    # print(encrypt_mixed)
    # decrypt_mixed = decrypt(aes_key, encrypt_mixed)
    # print(decrypt_mixed)
    # print(decrypt_mixed == mix_16)
