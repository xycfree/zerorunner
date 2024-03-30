#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/6/17 17:32  @Author: xycfree  @Descript: 病毒、漏洞库文件爬取
import os.path
import re
import subprocess
from datetime import datetime

from autotest.init import logger
from autotest.schemas.api.leaks_query import LeakfixIn
from autotest.services.api.leakfix import LeakfixService
from autotest.utils.emails import send_email
from autotest.utils.leak_scan_config import leak_infos
from autotest.utils.leakfix_scan_util import get_file_md5, get_file_size, down_file_move
from autotest.utils.licinfo_scan_task import get_licinfo_scan
from autotest.utils.locker import file_lock, file_unlock
from autotest.utils.utils import stat_info, match_datetime, read_ini, cabextract_info
from config import config as conf


async def leak_task():
    # if not file_lock():
    #     return

    try:
        li = []
        logger.info("病毒库、漏洞库执行批量操作...")

        # stat文件modify时间为当前时间，需要通过wget下载的文件列表
        wget_list = ['UpdateList.xml', 'bfupdate.ini', 'bfup.ver.ini', "xc_bfupdate.ini", "xc_bfupdate1.ini", "index.db",
                     "HotEvents.zip", "bfupvndt.ini", "edr_cloud.xml.tar.gz", "avlib_win1.zip", "avlib_win2.zip"]
        for k, v in leak_infos.items():
            try:
                # 文件下载，统一通过wget下载
                target_path = os.path.join(conf.DOWNLOAD_FILES_DIR, k)
                # reuqests和wget下载文件后stat文件的modify 时间会显示为当前下载时间，需要通过linux下的wget解决
                # os.system(f"wget {v['url']} -O {target_path}")
                wget_result = subprocess.Popen(f"/usr/bin/wget {v['url']} -O {target_path}", shell=True,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)  # 使用管道
                # logger.info(f"wget下载文件:{k}, 下载结果: {wget_result.stdout.read()}.")

                if "ERROR" in wget_result.stdout.read().decode('utf-8'):
                    logger.error(f"{k}下载异常!")
                    res, file_path = False, ""
                else:
                    logger.info(f"wget下载文件:{k},下载成功")
                    res, file_path = True, target_path

                di = {}

                if not res:
                    di.update({"url": v['url'], "name": v['name'], "md5": "", "update": "", "days": "", "last_time": "",
                               "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "remark": file_path,
                               "status": 0})
                    li.append(di)
                    continue

                if ".cab" in v['name']:  # .cab解压文件
                    # 解压cab文件
                    md5, size, c_time = execute_cab_file(v['name'], v['url'], file_path, di, li)  # 解压处理处理cab文件
                    logger.info(f"cab文件解压:{v['name']}, md5:{md5}, size:{size}, c_time:{c_time}")
                elif v['name'] in wget_list:  # stat获取文件的modify date
                    # stat获取'UpdateList.xml', 'bfupdate.ini'文件modify时间
                    res, ini_info = stat_info(file_path)
                    md5 = get_file_md5(file_path)  # ini_path
                    size = get_file_size(file_path)  # ini_path
                    c_time = match_datetime(ini_info)[1]  # access modify change
                    logger.info(f"文件stat:{v['name']}, md5:{md5}, size:{size}, c_time:{c_time}")
                else:  # 读取ini文件的日期
                    md5 = get_file_md5(file_path)
                    size = get_file_size(file_path)
                    config = read_ini(file_path)
                    c_time = config.get("product.ver", "date")
                    if len(c_time) == 10:
                        c_time += " 00:00:00"
                    logger.info(f"读取bfup.ver.ini, {v['name']}, md5:{md5}, size:{size}, c_time:{c_time}")

                info = await LeakfixService.get_leakfix_by_name(v['name'])  # 倒序排序获取第一条数据
                # info = info.dict(exclude_unset=True) if info else {}  # exclude_unset去掉默认字段

                logger.info(f"name:{v['name']},查询最近一条数据:{info}")
                _md5 = info.get("md5", "")

                # 根据md5为空、新旧md5不一致、文件创建时间与当前时间一致
                if not _md5 or _md5 != md5 or c_time.split()[0] == datetime.now().strftime("%Y-%m-%d"):
                    logger.info(
                        f"文件更新，文件名:{v['name']}, 更新时间:{c_time}" if _md5 else f"文件为新增:{v['name']}初次新增数据,创建时间:{c_time}")

                    # 文件移动到对应的目录下
                    logger.info(f"下载文件进行移动，文件名:{v['name']}, 当前路径:{file_path}")
                    res, new_path = down_file_move(v['name'], file_path, c_time)
                    # logger.info(f"文件移动结果:{res},文件名:{v['name']}，移动路径:{new_path}")
                    if res:
                        leak = LeakfixIn(
                            name=v['name'],
                            url=v['url'],
                            size=size,
                            addr=new_path,
                            c_time=c_time,
                            remark="",
                            md5=md5
                        )
                        leak_res = LeakfixService.save_or_update(leak)  # 新增
                        logger.info(f"文件新增入库，文件: {v['name']}, 入库结果: {leak_res}")
                        _days = (datetime.now() - datetime.strptime(c_time, "%Y-%m-%d %H:%M:%S"))
                        # datetime.timedelta(days=5, seconds=61967, microseconds=944462)
                        _days = _days.days + 1 if _days.seconds / 3600 > 0.5 else _days.days
                        di.update(
                            {"url": v['url'], "name": v['name'], "md5": md5, "update": True, "days": _days,
                             "last_time": datetime.strptime(c_time, "%Y-%m-%d %H:%M:%S"),
                             "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "remark": "更新", "status": 1})
                    else:
                        logger.error(f"文件:{v['name']},移动失败,原因：{new_path}")
                        di.update(
                            {"url": v['url'], "name": v['name'], "md5": md5, "update": "", "days": "",
                             "last_time": datetime.strptime(c_time, "%Y-%m-%d %H:%M:%S"),
                             "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             "remark": "下载文件移动异常:{}".format(new_path), "status": 1})

                else:
                    _days = (datetime.now() - info[
                        "c_time"])  # datetime.timedelta(days=5, seconds=61967, microseconds=944462)
                    _days = _days.days + 1 if _days.seconds / 3600 > 0.5 else _days.days
                    update_status = "有更新" if _days <= v['remind_day'] else "未更新"
                    logger.info(f"文件名称: {v['name']},更新状态: {update_status}")
                    try:
                        last_time = datetime.strftime(info.get("c_time", ""), "%Y-%m-%d %H:%M:%S")
                    except:
                        last_time = ""

                    di.update(
                        {"url": v['url'], "name": v['name'], "md5": md5, "update": False, "days": _days,
                         "last_time": last_time,
                         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "remark": update_status,
                         "status": 1})
                li.append(di)
            except Exception as e:
                logger.error(f"病毒库、漏洞库执行失败: {str(e)}")
            finally:
                pass
        # logger.info("本次定时任务获取的数据如下:{}".format(li))
        logger.info("授权文件信息监控...")
        result = await get_licinfo_scan()

        mail(li, lic=result)
    except Exception as e:
        logger.error(f"leak_task方法异常：{str(e)}")

    # file_unlock()


def execute_cab_file(name, url, file_path, di, li):
    """ 处理扩展名为cab文件
    :return:
    """
    try:
        res, s = cabextract_info(file_path)  # 解压cab文件
        logger.debug(f"解压cab文件:{name}, 结果:{res}, 信息:{s}")
        if not res:
            logger.exception(f"cab文件:{name},解压异常:{s}")
            di.update(
                {
                    "url": url, "name": name, "md5": "", "update": "", "days": "", "last_time": "",
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "remark": s,
                    "status": 0
                }
            )
            li.append(di)
            return "", "", ""

        # cab_name = re.findall(":.*.cab", s, re.S)[0].split(" ")[-1]
        ini_name = re.findall("extracting.*.ini", s, re.S)[0].split(" ")[-1]  # 获取cab文件解压后的ini文件
        ini_path = os.path.join(file_path.rsplit('/', 1)[0], ini_name)  # ini文件路径

        # stat 查看ini文件信息
        res, ini_info = stat_info(ini_path)
        logger.info(f"stat文件:{ini_path}, 结果:{res}, 消息:{ini_info}")
        if not res:
            logger.exception(f"文件stat异常:{ini_info}")
            di.update({"url": url, "name": name, "md5": "", "update": "", "days": "", "last_time": "",
                       "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "remark": ini_info,
                       "status": 0})
            li.append(di)
            return "", "", ""

        md5 = get_file_md5(file_path)  # ini_path
        size = get_file_size(file_path)  # ini_path

        if name == "qex.ini.cab":  # 处理mac 时间需要从qex.ini中取
            config = read_ini(ini_path)
            c_time = config.get("qex", "libdate")
            if len(c_time) == 10:
                c_time += " 00:00:00"
        else:
            c_time = match_datetime(ini_info)[1]  # access modify change

        os.system(f"rm -f {ini_path}")
        return md5, size, c_time
    except Exception as e:
        logger.error(f"解压cab文件异常:{str(e)}")
        return "", "", ""



def mail(info, lic=""):
    # s = "<br>{}未更新天数:[{}]</br>"
    ss = ""
    # for t in info:
    #     ss += s.format(t["name"], t["days"])
    if lic:
        ss += "<br>-------------------------------------</br>"
        ss += f"授权文件监控结果: {lic[-1]}"
        ss += "<br>-------------------------------------</br>"

    # logger.info(f"邮件发送:{info}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # %H:%M:%S
    # file = os.path.join(os.getcwd(), "db.sqlite3")
    send_email(info, now_time=now, remark=ss)


if __name__ == '__main__':
    leak_task()
    # demo_db()
