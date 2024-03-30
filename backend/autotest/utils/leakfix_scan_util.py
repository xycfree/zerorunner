#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/6/17 15:57  @Author: xycfree  @Descript: 漏洞库更新扫描
import hashlib
import os
import re
import shutil
import subprocess

import requests
import time

from loguru import logger
# note that requests.packages.urllib3 is just an alias for urllib3
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from autotest.utils import down_dirs
from autotest.utils.leak_scan_config import leak_infos

disable_warnings(InsecureRequestWarning)

sess = requests.Session()


def time_stamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def get_download_file(url, method='GET', name='', path='', param=None, data=None, header=None, cookie=None, timeout=10,
                      retry=3, proxies=None, verify=None, stream=None):
    """文件下载 return: 下载结果，文件path or 错误原因"""
    err_info = ""

    # 通过上下文处理
    while retry:
        try:
            if re.match(r'^https://', url):
                verify = False
            r = sess.request(method, url, params=param, data=data, headers=header, cookies=cookie, timeout=timeout,
                             proxies=proxies, verify=verify, stream=stream)
            if r.status_code != 200:
                logger.warning('请求Url:{} status: {},重新请求!'.format(r.url, r.status_code))
                err_info = r.content.decode('utf-8')
                retry -= 1
                continue

            _dir = path or down_dirs.down_path
            name = name or url.split("/")[-1]

            make_dirs(_dir)  # 判断路径是否存在，不存在则创建路径

            file_path = os.path.join(_dir, name)
            logger.info(f"下载文件路径:{file_path}")

            with open(file_path, mode='wb') as fd:
                for chunk in r.iter_content(4096):
                    fd.write(chunk)
            logger.info('{}下载完成.'.format(name))
            return True, file_path
        except Exception as e:
            logger.exception("下载异常: {}".format(e))
            # return False, str(e)
            retry -= 1
    return False, f"url地址请求异常:{err_info}"


def get_file_md5(fname):
    m = hashlib.md5()  # 创建md5对象
    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象
    return m.hexdigest()  # 返回md5对象


def get_file_size(fname):
    """获取文件的大小,结果保留两位小数，单位为MB"""
    fsize = os.path.getsize(fname)
    # fsize = fsize / float(1024 * 1024)  # MB
    fsize = fsize / float(1024)  # KB
    return round(fsize, 2)


def get_file_access_time(fname):
    """获取文件的访问时间"""
    t = os.path.getatime(fname)
    return time_stamp_to_time(t)


def get_file_create_time(fname):
    """获取文件的创建时间"""
    t = os.path.getctime(fname)
    return time_stamp_to_time(t)


def get_file_modify_time(fname):
    """获取文件的修改时间"""
    t = os.path.getmtime(fname)
    return time_stamp_to_time(t)


def down_file_move(name, file_path, ctime):
    """ 文件移动至对应目录
    :param name: 文件名称
    :param file_path: 文件路径
    :param ctime: 当前时间 yyyy-mm-dd
    :return:
    """

    try:
        ctime = ctime.split()[0]
        down_dir = leak_infos[name]['download_path']  # 获取文件初始下载目录
        logger.info(f"下载文件移动, 文件名:{name}, 文件原路径:{file_path}, 目标路径:{down_dir}")

        new_dir = os.path.join(down_dir, ctime)
        logger.info(f"创建目录: {new_dir}")
        resu = make_dirs(new_dir)
        if not resu:
            return False, f"文件:{name},移动失败"

        if os.path.exists(os.path.join(new_dir, name)):
            os.remove(os.path.join(new_dir, name))

        res = shutil.move(file_path, new_dir)
        logger.info(f"文件:{name}, 移动至新目录: {new_dir}, 移动结果:{res}")
        return True, res
    except Exception as e:
        logger.error(f"文件{name},移动失败:{e}")
        return False, str(e)


def make_dirs(file_path):
    """ 创建目录，os.makedirs() 方法用于递归创建目录。
    :param file_path:
    :return:
    """
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
            logger.info(f"创建目录:{file_path}, 创建成功.")
        return True
    except Exception as e:
        logger.error(f"创建目录失败:{str(e)}")
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