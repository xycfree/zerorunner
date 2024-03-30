#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024/1/3 16:43 __walter__ @Desc: 文件锁
# import fcntl   # 文件锁，不支持windows
import os

import portalocker  # 文件锁，跨平台


# curr_path = Path.cwd()  # 获取当前目录 WindowsPath('D:/spider/epp_locust')
# home_path = Path.home()  # 获取用户目录
# file_path = Path(__file__).resolve()  # 文件当前路径
# curr_file_path = Path.cwd().joinpath(f_path)  # 合并join

import pathlib
from autotest.init import  logger

file_path = pathlib.Path(__file__).parent.parent.joinpath("config/flag.lock")
# D:\\spider\\360\\zerorunner\\backend\\autotest\\config\\flag.lock
if not pathlib.Path.exists(file_path):
    file_path.touch()


def file_lock():
    with pathlib.Path.open(file_path, "r+", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
        """
        fcntl.LOCK_SH: 共享锁, 所有进程对当前文件都没有写权限, 即使加锁的进程也没有, 但是都具有读权限;
        fcntl.LOCK_EX: 排它锁, 除了加锁进程具有当前文件的读写权限之外, 其它的进程都没有;
        fcntl.LOCK_UN: 对加锁文件进行解锁;
        fcntl.LOCK_MAND: 共享模式强制锁, 可以和 LOCK_READ 或者 LOCK_WRITE 联合起来使用, 从而表示是否允许并发的读操作或者并发的写操作(基本不用);
        fcntl.LOCK_NB: 非阻塞锁, 如果指定此参数, 函数不能获得文件锁就立即返回; 否则, 函数会等待获得文件锁, LOCK_NB 可以同 LOCK_SH、LOCK_EX 进行按位或操作;
        """

        data = f.read().strip()
        if str(data) == "0":
            logger.info("文件非加锁,进行加锁...")
            f.seek(0)
            f.truncate()
            f.write("1")
            f.flush()
            os.fsync(f.fileno())
            return True
        else:
            logger.info("文件已加锁")
            return False


def file_unlock():
    with pathlib.Path.open(file_path, "r+", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LockFlags.UNBLOCK)
        """
        fcntl.LOCK_SH: 共享锁, 所有进程对当前文件都没有写权限, 即使加锁的进程也没有, 但是都具有读权限;
        fcntl.LOCK_EX: 排它锁, 除了加锁进程具有当前文件的读写权限之外, 其它的进程都没有;
        fcntl.LOCK_UN: 对加锁文件进行解锁;
        fcntl.LOCK_MAND: 共享模式强制锁, 可以和 LOCK_READ 或者 LOCK_WRITE 联合起来使用, 从而表示是否允许并发的读操作或者并发的写操作(基本不用);
        fcntl.LOCK_NB: 非阻塞锁, 如果指定此参数, 函数不能获得文件锁就立即返回; 否则, 函数会等待获得文件锁, LOCK_NB 可以同 LOCK_SH、LOCK_EX 进行按位或操作;
        """

        data = f.read().strip()
        if str(data) == "1":
            logger.info("文件已加锁，进行解锁..")
            f.seek(0)
            f.truncate()
            f.write("0")
            f.flush()
            os.fsync(f.fileno())
            return True
        else:
            logger.info("文件非加锁")
            return False