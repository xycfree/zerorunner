#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/10/29 14:20  @Author: wangbing3  @Descript:
import json
import os
import re
import time
import requests
from typing import Optional, Dict, Any, List, Text
from loguru import logger

sess = requests.Session()


def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def get_request(url: str, method: str = 'GET', params: Optional[Dict] = None,
                data: Optional[Dict] = None, json: Optional[Any] = None,
                headers: Optional[Dict] = None, cookie: Optional[Any] = None,
                timeout: int = 10, retry: int = 3, proxies: str = None,
                verify: bool = None, stream: bool = None, file_path: str = "", file_name: str = "",
                ):
    """requests 请求 get/post, 默认重试三次"""
    # sess.headers = headers
    err_info = "请求异常"
    while retry:
        try:
            if re.match(r'^https://', url):
                verify = False
            r = sess.request(method, url, params=params, data=data, headers=headers, cookies=cookie, timeout=timeout,
                             json=json, proxies=proxies, verify=verify, stream=stream)
            if r.status_code != 200:
                logger.warning(f'请求Url:{r.url} status: {r.status_code}, content: {r.content.decode("utf-8")}, 重新请求!')
                err_info = r.content.decode('utf-8')
                retry -= 1
                continue
            if stream:
                file_path = file_path or os.getcwd()  # 下载地址或者当前目录
                _path = os.path.join(file_path, file_name)
                with open(_path, mode='wb') as fd:
                    for chunk in r.iter_content(4096):
                        fd.write(chunk)
                return True, _path
            else:
                result = r.content.decode("utf-8")
                return True, result
        except Exception as e:
            logger.exception("请求异常: {}".format(str(e)))
            err_info = "请求异常"
    return False, err_info


def get_request_data(r) -> dict:
    """ 根据request Response获取内容
    :param r: Response
    :return:
    """
    data = r.content.decode("utf-8")
    return data if isinstance(data, dict) else json.loads(data)



if __name__ == '__main__':
    url = "https://github.com/wilzokch/mysql-log-filter/blob/master/mysql_filter_slow_log.py"
    res, data = get_request(url, method='get', stream=True, file_name="mysql_filter_slow_log.py")
    print(res, data)
