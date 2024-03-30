#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/9/23 16:41  @Author: xycfree  @Descript:
import os
from pathlib import Path

from autotest.utils.leak_scan_config import leak_infos
from config import config

down_path = config.DOWNLOAD_FILES_DIR

if not os.path.exists(config.DOWNLOAD_FILES_DIR):
    # Path.mkdir(config.DOWNLOAD_FILES_DIR)
    Path(config.DOWNLOAD_FILES_DIR).mkdir(parents=True)  # 创建多层

li = [v['download_path'] for k, v in leak_infos.items()]

# 下载目录判断，不存在则创建
for p in li:
    if not os.path.exists(p):
        os.mkdir(p)


def create_down_path(file_name: str, ctime: str) -> str:
    """ 根据文件名，更新时间创建文件目录
    :param file_name: 文件名
    :param ctime: 更新时间
    :return:
    """
    _name = file_name.split(".")[0]
    for i in li:
        if _name in i:
            _path = os.path.join(i, ctime)
            if os.path.exists(_path):
                os.mkdir(_path)
            return _path
    return ""


def get_down_path(file_name: str, ctime: str) -> str:
    """ 根据文件名称获取下载目录路径
    :param ctime: 文件所在目录，根据时间创建目录
    :param file_name: 文件名称
    :return:
    """
    _name = file_name.split(".")[0]
    for i in li:
        if _name in i:
            return os.path.join(i, ctime, file_name)
    return ""


if __name__ == '__main__':
    s = get_down_path("360exthost.cab", "2021-09-21")
    print(s)

"""
360exthost.cab未更新天数:[3]

sdupbd.cab未更新天数:[2]

bfup.ver.ini未更新天数:[1]

qex.ini.cab未更新天数:[20]

win7shield.cab未更新天数:[7]

kplib.cab未更新天数:[3]

"""
