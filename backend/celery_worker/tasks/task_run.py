# -*- coding: utf-8 -*-
# @author: walter
import typing

from autotest.schemas.api.timed_task import TaskKwargsIn
from celery_worker.worker import celery
from celery_worker.tasks.ui_case import async_run_ui
from celery_worker.tasks.test_case import async_run_testcase
from loguru import logger
from celery_worker.tasks.monitor_case import sync_server_all_task, leakfix_scan_task, licinfo_scan_task



@celery.task(name="zerorunner.batch_async_run_testcase")
def batch_async_run_testcase(**kwargs: typing.Any):
    """批量执行"""
    params = TaskKwargsIn(**kwargs)
    if params.case_ids:
        kwargs['run_type'] = "case"
        for api_id in params.case_ids:
            async_run_testcase.apply_async(args=[api_id], kwargs=kwargs, __business_id=api_id)
    if params.ui_ids:
        kwargs['run_type'] = "ui"
        for ui_id in params.ui_ids:
            async_run_ui.apply_async(args=[ui_id], kwargs=kwargs, __business_id=ui_id)


@celery.task(name="zerorunner.batch_async_run_monitor_func")
def batch_async_run_monitor_func(**kwargs: typing.Any):

    params = TaskKwargsIn(**kwargs)
    logger.info(f"执行batch_async_run_monitor_func,task_name:{params.name}")
    var = globals()[params.name].apply_async()
    logger.info(f"var:{var}, task_name:{params.name}执行结束!")


