#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/11/18 14:47  @Author: wangbing3  @Descript:

import codecs
# from Crypto.Cipher import ARC4  # pip失败，需要安装visual C++文件...
from Cryptodome.Cipher import ARC4  # pip install pycryptodomex

import base64

MOD = 256


def KSA(key):
    """
    Key Scheduling Algorithm (from wikipedia):
        for i from 0 to 255
            S[i] := i
        endfor
        j := 0
        for i from 0 to 255
            j := (j + S[i] + key[i mod keylength]) mod 256
            swap values of S[i] and S[j]
        endfor
    """
    key_length = len(key)
    # create the array "S"
    S = list(range(MOD))  # [0,1,2, ... , 255]
    j = 0
    for i in range(MOD):
        j = (j + S[i] + key[i % key_length]) % MOD
        S[i], S[j] = S[j], S[i]  # swap values
    print(f"KSA, S: {S}")
    return S


def PRGA(S):
    """
    Psudo Random Generation Algorithm (from wikipedia):
        i := 0
        j := 0
        while GeneratingOutput:
            i := (i + 1) mod 256
            j := (j + S[i]) mod 256
            swap values of S[i] and S[j]
            K := S[(S[i] + S[j]) mod 256]
            output K
        endwhile
    """
    i = 0
    j = 0
    while True:
        i = (i + 1) % MOD
        j = (j + S[i]) % MOD

        S[i], S[j] = S[j], S[i]  # swap values
        K = S[(S[i] + S[j]) % MOD]
        yield K


def get_keystream(key):
    """
    Takes the encryption key to get the keystream using PRGA
    return object is a generator
    """
    print(f"get_keystream: {key}")
    S = KSA(key)
    return PRGA(S)


def encrypt_logic(key, text):
    """
    :key -> encryption key used for encrypting, as hex string
    :text -> array of unicode values/ byte string to encrpyt/decrypt
    """
    # For plaintext key, use this
    key = [ord(c) for c in key]
    keystream = get_keystream(key)

    res = []
    for c in text:
        val = ("%02X" % (c ^ next(keystream)))  # XOR and taking hex
        res.append(val)
    return ''.join(res)


def encrypt(key, plaintext):
    """
    :key -> 加密key
    :plaintext -> 加密内容
    """
    plaintext = [ord(c) for c in plaintext]
    return encrypt_logic(key, plaintext)


def decrypt(key, ciphertext):
    """
    :key -> 加密key
    :ciphertext -> 十六进制编码密文使用RC4
    """
    ciphertext = codecs.decode(ciphertext, 'hex_codec')
    res = encrypt_logic(key, ciphertext)
    # print(res)
    return codecs.decode(res, "hex_codec").decode('utf-8')


def rc4_encrypt(data, key1):  # 加密
    key = bytes(key1, encoding='utf-8')
    enc = ARC4.new(key)
    res = enc.encrypt(data.encode('utf-8'))
    res = base64.b64encode(res)
    res = str(res, 'utf-8')
    return res


def rc4_decrypt(data, key1):  # 解密
    data = base64.b64decode(data)
    key = bytes(key1, encoding='utf-8')
    enc = ARC4.new(key)
    res = enc.decrypt(data)
    res = str(res, 'utf-8')
    return res


if __name__ == '__main__':
    s = encrypt("lkjhhgtyuik", "sn=T8W9N-95JRD-P8J8C-AYA8L-VW9GS&pid=Ent_360EPP288719845&pwd=")
    print(f"加密：{s}")  # 加密

    ss = decrypt("lkjhhgtyuik",
                 "9013591CC491882A2D3F0E62964B633FF25BC1513C17F7886972D3703DD50E781F6DC0C86CBBC0C13451E6A92B4FD7CF277A99B1849047FE87207CFCBC")
    print(f"解密: {ss}")  # 解密
    print("------------------")

    data = 'sn=T8W9N-95JRD-P8J8C-AYA8L-VW9GS&pid=Ent_360EPP288719845&pwd='  # 需要加密的内容
    key = 'lkjhhgtyuik'  # 加密key
    encrypt_data = rc4_encrypt(data, key)  # 加密方法
    print('加密后:', encrypt_data)
    print('解密后:', rc4_decrypt(encrypt_data, key))  # 解密方法
