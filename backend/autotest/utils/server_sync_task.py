#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2022/11/3 19:35  @Author: wangbing3  @Descript: 服务器配置信息任务
import asyncio
from concurrent.futures import ThreadPoolExecutor


from loguru import logger

from autotest.utils.server_ver_operate import ServerInfo
from config import config
from autotest.schemas.api.serverip_query import ServerIpIn
from autotest.services.api.server_ip import ServerIPService


async def sync_server_info(id: int, ip: str, name: str):
    """ 同步服务器信息
    :param name: name
    :param id: 数据id
    :param ip: IP
    :return:
    """
    username = config.SERVER_USER
    password = config.SERVER_PASS
    user = ServerInfo(ip, username, password)
    conn_status = user.connect()
    if not conn_status:
        logger.error(f"[ssh] host: {ip}, 连接失败，请检查用户[{username}]是否有该服务器权限")
        return

    _, cpu = user.get_cpu_info()
    _, mem = user.get_free_info()
    _, disk_total, disk_use = user.get_disk_info()
    _, epp_install_version = user.get_epp_version()
    if epp_install_version:
        server_users = ','.join(user.get_user_info())  # list to str
        epp_install_status = user.get_epp_install()["status"]

        epp_run_status = user.get_epp_run()["status"]
        epp_is_multi, center_data = user.get_epp_multi()
    else:
        server_users = ""
        epp_install_status = 1
        epp_run_status = 0
        epp_is_multi, center_data = {"status": 0, "msg": "未知"}, []
    # db: Session = get_session()
    logger.debug(f"epp_is_multi, center_data: {epp_is_multi},  {center_data}")

    data = ServerIpIn(
        id=id,
        name=name,
        ip=ip,
        cpu=cpu,
        mem=mem,
        disk_use=disk_use,
        server_users=server_users,
        disk_total=disk_total,
        is_install=epp_install_status,
        is_run=epp_run_status,
        is_multi=epp_is_multi.get("status", 0),
        epp_version=epp_install_version,
        # remark=str(center_data)
    )
    try:
        logger.info(f"服务器: {ip}, 同步资源数据获取: {data}")
        await ServerIPService.save_or_update(data)
        
        logger.info(f"服务器:{ip}, 资源同步已完成.")
    except Exception as e:
        logger.error(f"服务器: {ip}, 资源同步失败: {str(e)}")


async def sync_server_all():
    logger.info("[sync] 开始同步服务器资源信息...")
    data = await ServerIPService.get_all()
    with ThreadPoolExecutor(max_workers=5) as executor:  # 多任务处理
        for i in data:
            try:
                _id = i.get('id')
                ip = i.get("ip")
                name = i.get("name")
                # future = executor.submit(sync_server_info, _id, ip)
                await asyncio.gather(
                    sync_server_info(_id, ip, name),
                )
                # sync_server_info(_id, ip)
            except Exception as e:
                logger.exception(f"[sync] 服务器同步失败: {str(e)}")
    logger.info("[sync] 同步服务器资源信息结束!")


if __name__ == '__main__':
    sync_server_info(3, "10.217.62.234")