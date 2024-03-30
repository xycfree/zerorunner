#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/6/28 16:29  @Author: xycfree  @Descript:
import os

import math
import re
import subprocess
from configparser import ConfigParser
from datetime import datetime

import IPy as IPy
from loguru import logger
from functools import wraps
from config import config


class InstanceClass(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InstanceClass, cls).__new__(cls, *args, **kwargs)
        return cls._instance


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


def match_date(text):
    """正则表达式提取文本所有日期
    :param text: 待检索文本
    >>> match_date('日期是2020-05-20 13:14:15.477062.')
    ['2020-05-20']
    """
    pattern = r'(\d{4}-\d{1,2}-\d{1,2})'
    pattern = re.compile(pattern)
    result = pattern.findall(text)
    return result


def match_datetime(text):
    """正则表达式提取文本所有日期+时间
    :param text: 待检索文本
    >>> match_datetime('日期是2020-05-20 13:14:15.477062.')
    ['2020-05-20 13:14:15']
    """
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})'
    pattern = re.compile(pattern)
    result = pattern.findall(text)
    return result


def match_ip(text):
    """ 匹配字符串中是否存在合规的IP地址
    :param text:
    :return: list
    """
    pattern = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))")
    result = pattern.findall(text)
    return result


def check_ip(ip_addr):
    """ 检查ip_addr 是否为合规的IP地址
    :param ip_addr:
    :return:
    """
    compile_ip = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ip_addr):
        return True
    else:
        return False


def is_ip(address):
    """ 检查IP地址是否合规，使用IPy包
    :param address:
    :return:
    """
    try:
        IPy.IP(address)
        return True
    except ValueError as e:
        logger.error(f"IP地址:{address}不合法,错误原因:{str(e)}!")
        return False


def cabextract_info(source, target=""):
    """ 解压cab包，linux环境
    :param source: 源文件
    :param target: 目标目录, 默认为空，解压至当前目录
    :return: 解压信息
    """
    # 解压cab文件
    _target = target if target else source.rsplit('/', 1)[0]
    cmd = f"/usr/bin/cabextract {source} -d {_target}"
    try:
        # os.system("cabextract {}".format(name))
        # ss = os.popen("cabextract {}".format(name))
        s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        s = s.stdout.read().decode("utf-8")
        return True, s
    except Exception as e:
        logger.error(f"执行命令cabextrat:{cmd}错误，错误信息:{str(e)}")
        return False, str(e)


def stat_info(file_path):
    # stat 查看ini文件信息
    cmd = f"/usr/bin/stat {file_path}"
    try:
        ini_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ini_info = ini_info.stdout.read().decode("utf-8")
        return True, ini_info
    except Exception as e:
        logger.error(f"执行命令stat:{cmd}错误, 错误信息:{str(e)}")
        return False, str(e)


def read_ini(file_path):
    config = ConfigParser()
    config.read(file_path, encoding='utf-8')
    return config


def time_to_datetime(ctime, formats="%Y-%m-%d %H:%M:%S"):
    """ 时间戳转换为datetime
    :param ctime:
    :param formats: datetime格式化
    :return:
    """
    t = datetime.fromtimestamp(ctime)
    t = t.strftime(formats)
    return t


def pagenation(record, page: int, count: int, size: int = 20):
    """ 前后端不分离 分页方法
    :param size: 每页显示数据条数
    :param record: 记录数据
    :param page: 当前页
    :param count: 总数
    :return:
    """
    # total_page = count // page_size + 1 if count % page_size else count // page_size
    total_page = math.ceil(count / size)

    next_url = f"?page={page + 1}&size={size}" if (page + 1) <= total_page else "null"
    pre_url = f"?page={page - 1}&size={size}" if (page - 1) >= 1 else "null"

    if page == 0:
        page = 1

    if page >= total_page:
        page = total_page

    return {
        'count': count,
        'curr_page': page,
        'total_page': total_page,
        'next_url': next_url,
        'pre_url': pre_url,
        "data": record,
        "size": size
    }


def disk_unit_conversion(data: str) -> float:
    """ 磁盘单位转换 如1.4T  400G  500M 转换为G
    :param data: 含单位 400G
    :return:
    """
    d, d_unit = data.strip()[:-1], data.strip()[-1]
    if d_unit.upper() == "G":
        return float(d)
    elif d_unit.upper() == "M":
        return float(d) / 1024
    elif d_unit.upper() == "T":
        return float(d) * 1024
    return float(d)


if __name__ == '__main__':
    # res = is_ip("10.202.253.11 d")
    # print(res)
    # import pathlib
    _path = os.path.join(config.BASE_PATH, 'core', 'config', 'pro.env.ini')

    res = read_ini(_path)
    print(f"res: {res.get('mysql', 'MYSQL_USERNAME')}, type:{type(res)}")