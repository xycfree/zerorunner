#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/11/18 14:47  @Author: wangbing3  @Descript:
import json
import os, sys

from loguru import logger

from autotest.utils.crypto_rc4 import rc4_encrypt
from autotest.utils.request import get_request

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_path)



HOST = "http://dlc.360.cn"


async def get_licinfo_scan():
    key = "lkjhhgtyuik"
    sn = "CKCHY-NUV2E-HR9TS-YSGH9-U79BP"
    pid = "360EPP1342412222"  # Ent_360EPP1342412222 没有Ent_
    pwd = ""
    text = f"sn={sn}&pid={pid}"  # &pwd={pwd}
    _id = rc4_encrypt(text, key)
    logger.info(f"id: {_id}")
    resu = get_register(_id)
    logger.info(f"获取token信息: {resu}")
    if resu.get("errno") != 0:
        return False, f"sn:{sn}, 获取token失败: {resu}"

    token = resu.get("token")

    # res = get_chect_token(token)
    # logger.info(f"check_token: {res}")

    res = get_relation(token)
    logger.info(f"relation: {res}")

    if res.get("errno") != 0:
        return False, f"sn:{sn}, 获取授权文件信息失败: {res}"

    # res = get_unregister(token)
    # logger.info(f"unregiste: {res}")

    return check_update(res, sn)



def get_register(_id):
    """ 注册获取token
    :param _id: sn={sn}&pid={pid}  rc4加密
    :return:
    """
    url = f"{HOST}/api/auth/register"
    flag, result = get_request(url, method="post", data={"id": _id})
    result = result if isinstance(result, dict) else json.loads(result)
    return result


def get_chect_token(token):
    """ 检查token
    :param token:
    :return:
    """
    url = f"{HOST}/api/auth/check"
    flag, result = get_request(url, method="post", data={"token": token})
    result = result if isinstance(result, dict) else json.loads(result)
    return result


def get_unregister(token):
    """ 注销token
    :param token:
    :return:
    """
    url = f"{HOST}/api/auth/unregister"
    flag, result = get_request(url, method="post", data={"token": token})
    result = result if isinstance(result, dict) else json.loads(result)
    return result


def get_relation(token):
    """ 获取授权文件数据
    :param token:
    :return:
    """
    url = f"{HOST}/api/auth/relation/?token={token}"
    flag, result = get_request(url, method="get")
    result = result if isinstance(result, dict) else json.loads(result)
    return result


def check_update(result, sn):
    """ 检查授权文件 data数据中是否含有update为1970-01-01的数据
    :param sn:
    :param result:
    :return:
    """
    li = []
    result = result if isinstance(result, dict) else json.loads(result)
    data = result.get("data")
    relation = data.get("relation")
    for i in relation:
        update = i.get("update", "")
        if update == "":
            continue
        if update == "1970-01-01":
            li.append(i)
    if li:
        return False, f"sn:{sn}, 监控update存在异常: {li}"
    return True, f"sn: {sn}, 校验通过,Success!"


if __name__ == '__main__':
    res = get_licinfo_scan()
    logger.info(f"结果: {res}")
