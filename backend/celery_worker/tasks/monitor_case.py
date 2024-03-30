#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024/2/26 15:50 __walter__ @Desc:
import time


from loguru import logger

from autotest.utils.leak_scan_task import leak_task
from autotest.utils.licinfo_scan_task import get_licinfo_scan
from autotest.utils.server_sync_task import sync_server_all
from autotest.utils.utils import time_to_datetime
from celery_worker.worker import celery


@celery.task
async def sync_server_all_task(task_id: str = None):
    """
    异步执行接口
    :param : 执行参数
    :return:
    """
    logger.info(f"run task: sync_server_all_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    await sync_server_all()
    logger.info(f"task: sync_server_all_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")


@celery.task
async def leakfix_scan_task(task_id: str = None):
    """ 定时下载漏洞库、病毒库文件
    :param task_id:
    :return:
    """
    logger.info(f"run task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    await leak_task()
    logger.info(f"task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")


@celery.task
async def licinfo_scan_task(task_id: str = None):
    logger.info(f"run task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}")
    await get_licinfo_scan()
    logger.info(f"task: leakfix_scan_task, task_id:{task_id}, time:{time_to_datetime(time.time())}, end!")
