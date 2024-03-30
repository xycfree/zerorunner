#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/9/22 10:56  @Author: xycfree  @Descript:
"""
定时任务
"""

import time

from autotest.utils.leak_scan_task import leak_task
from autotest.utils.licinfo_scan_task import get_licinfo_scan
from autotest.utils.server_sync_task import sync_server_all
from autotest.utils.utils import time_to_datetime
from loguru import logger


def demo_task(task_id: str):
    t = time_to_datetime(time.time())
    logger.info(f"run task demo_task, task_id:{task_id}, time:{t}")


def leakfix_scan_task(task_id: str):
    """ 定时下载漏洞库、病毒库文件
    :param task_id:
    :return:
    """
    logger.info(f"run task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    leak_task()
    logger.info(f"task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")


def licinfo_scan_task(task_id: str):
    logger.info(f"run task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    get_licinfo_scan()
    logger.info(f"task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")


def sync_server_all_task(task_id: str):
    logger.info(f"run task: sync_server_all_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    sync_server_all()
    logger.info(f"task: sync_server_all_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")


fun_list = ["demo_task", "leakfix_scan_task", "licinfo_scan_task", "sync_server_all_task"]
# __all__ = ("fun_list", "demo_task", "leak_scan_task")


if __name__ == '__main__':
    s = "leakfix_scan_task"
    # print(locals()[s] in fun_list)
    var = locals()[s]
    var("aa")
