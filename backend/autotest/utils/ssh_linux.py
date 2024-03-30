#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2022/1/18 16:33  @Author: wangbing3  @Descript:
import os.path
from typing import Optional, List

import paramiko
import time
from paramiko import transport, client, sftp_client

from loguru import  logger
"""
https://docs.paramiko.org/en/2.4/api/client.html?highlight=connect
https://docs.paramiko.org/en/2.4/api/sftp.html
"""


# 定义一个类，表示一台远端linux主机
class SSHLinux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, host, username, password, timeout=30, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        self.ssh = None
        self.trans = None
        self.sftp = None
        # 链接失败的重试次数
        self.try_times = 1

    def connect(self):
        logger.info(f"[ssh] host:{self.host}进行连接...")
        while True:
            try:
                # 基于用户名和密码的 transport 方式登录
                self.trans = transport.Transport(self.host, self.port)  # 创建一个通道
                self.trans.connect(username=self.username, password=self.password)  # 连接

                self.ssh = client.SSHClient()  # 实例化SSHClient
                self.ssh.load_system_host_keys()  # 加载系统HostKeys密钥
                self.ssh._transport = self.trans
                # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
                self.ssh.set_missing_host_key_policy(client.AutoAddPolicy())

                self.sftp = sftp_client.SFTPClient.from_transport(self.trans)  # 实例化一个SFTPClient对象
                return True
            except Exception as e:
                if self.try_times > 0:
                    logger.error(f'[ssh] host:{self.host}连接失败: {str(e)}，进行重试...')
                    self.try_times -= 1
                else:
                    logger.error(f'[ssh] host:{self.host},重试连接失败，请检查网络和用户[{self.username}]是否有该服务器权限!')
                    return False

    def send(self, cmd):
        # get_pty=True 解决 nohup 执行了但是 进程没有启动成功
        # nohup 执行成功了，但是python程序阻塞了，无法停止，解决方式  nohup xx.xx  & sleep 1    &后增加sleep 1
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd, get_pty=True)
        try:
            sout = ssh_stdout.read().decode("utf-8").strip()
            if cmd not in ['sudo cat /etc/passwd', 'sudo docker ps']:
                logger.info(f"[ssh] {self.host}, {cmd}, stdout:{sout}")
            return True, sout
        except Exception as e:
            serr = ssh_stderr.read().decode("utf-8").strip()
            logger.error(f"[ssh] {self.host}, {cmd}, stderr:{serr}, {str(e)}")
            return False, serr

    def send_invoke_shell_msg(self, passwd: str, cmd: str):
        """ 切换为invoke_shell模式执行命令
        :param passwd:
        :param cmd:
        :return:
        """
        try:
            channel = self.ssh.invoke_shell()
            time.sleep(0.1)

            channel.send(f"sudo su \n")  # 切换为root
            buff = ''
            while not buff.endswith(f'[sudo] password for {self.username}: '):
                resp = channel.recv(9999)
                buff += resp.decode('utf-8')
                if buff.endswith("# "):  # 切换root不需要确认密码
                    logger.info(f"服务器:{self.host},切换root无需确认密码.")
                    break
            channel.send(passwd + "\n")
            # channel.send('\n')
            buff = ''
            while not buff.endswith('# '):  #  buff.endswith(('# ', '$ ')) 当指令执行结束后，Linux窗口会显示#，等待下条指令，所以可以用作识别全部输出结束的标志。
                resp = channel.recv(9999)
                buff += resp.decode('utf-8')
            logger.debug("------end------")

            # 查看是否切换成功
            channel.send(cmd)
            channel.send("\n")
            buff = ''
            while not buff.endswith('# '):
                resp = channel.recv(9999)
                buff += resp.decode('utf-8')
            return True, buff
        except paramiko.ssh_exception.AuthenticationException as e:
            logger.error(f'Failed to login. ip username or password not correct; {str(e)}')
            return False, str(e)

    def send_invoke_shell(self, passwd: str, cmd: str):
        """
        :param cmd:
        :param passwd:
        :return:
        """
        try:
            # 在command命令最后加上 get_pty=True，执行多条命令的话用;号隔开，另外所有命令都在一个大的单引号范围内引用
            std_in, std_out, std_err = self.ssh.exec_command(cmd, get_pty=True)
            std_in.write(passwd + '\n')  # 执行输入命令，输入sudo命令的密码，会自动执行
            li = []
            for line in std_out:
                s = line.strip('\n')
                li.append(s)
            s = "\n".join(li)
            logger.info(f"[ssh] {self.host}, {cmd}, stdout:{s}")
            return True, s
        except Exception as e:
            logger.error(f'send_invoke_shell 执行失败: {str(e)}')
            return False, str(e)

    def close(self):
        # 关闭连接
        self.trans.close()
        self.ssh.close()
        self.sftp.close()

    # SFTPClient
    def upload_file(self, local_path, remote_path):
        """ 文件上传
        :param local_path: 本地文件地址
        :param remote_path: 远程地址
        :return:
        """
        try:
            self.sftp.put(local_path, remote_path)
            logger.info(f"服务器:{self.host}, 文件: {remote_path.rsplit('/', 1)[-1]}上传成功.")
            return True
        except Exception as e:
            logger.error(f"文件:{remote_path.rsplit('/', 1)[-1]} 上传失败:{e}")
            return False

    def download_file(self, local_path, remote_path):
        """ 文件下载
        :param local_path: 本地要下载的目录
        :param remote_path: 远程文件地址
        :return:
        """
        try:
            self.sftp.get(remote_path, local_path)
            logger.info(f"服务器:{self.host}, 文件: {remote_path.rsplit('/', 1)[-1]}下载成功.")
            return True
        except Exception as e:
            logger.error(f"文件:{remote_path.rsplit('/', 1)[-1]} 下载失败:{e}")
            return False

    def update_chmod(self, path, mode=777):
        """ 文件权限修改 """
        try:
            self.sftp.chmod(path, mode)
            logger.info(f"服务器:{self.host}, 文件: {path}权限变更成功.")
            return True
        except Exception as e:
            logger.error(f"服务器:{self.host}, 文件: {path}权限变更失败: {e}.")
            return False

    def update_chown(self, path, uid, gid):
        """文件属主修改"""
        try:
            self.sftp.chown(path, uid, gid)
            logger.info(f"服务器:{self.host}, 文件: {path}属主变更成功.")
            return True
        except Exception as e:
            logger.error(f"服务器:{self.host}, 文件: {path}属主更新失败:{e}")
            return False

    def create_dir(self, path, mode=777):
        """新建文件夹"""
        if not os.path.exists(path):
            try:
                self.sftp.mkdir(path)
                logger.info(f"服务器:{self.host}, 文件夹: {path}创建成功.")
                return True
            except Exception as e:
                logger.error(f"服务器:{self.host}, 文件夹: {path}创建失败:{e}")
                return False

    def rm_dir(self, path):
        """删除文件夹"""
        try:
            self.sftp.rmdir(path)
            logger.info(f"服务器:{self.host}, 文件夹: {path}删除成功.")
            return True
        except Exception as e:
            logger.error(f"服务器:{self.host}, 文件夹: {path}删除失败:{e}")
            return False

    def remove_file(self, file_path):
        """删除文件"""
        try:
            self.sftp.remove(file_path)
            logger.info(f"服务器:{self.host}, 文件: {file_path}删除成功.")
            return True
        except Exception as e:
            logger.error(f"服务器:{self.host}, 文件: {file_path}删除失败:{e}")
            return False

    def rename_file(self, old_path, new_path):
        """文件重命名"""
        try:
            self.sftp.rename(old_path, new_path)
            logger.info(f"服务器:{self.host}, 文件: {new_path}重命名成功.")
            return True
        except Exception as e:
            logger.error(f"服务器:{self.host}, 文件: {new_path}重命名失败:{e}")
            return False

    def get_file(self, file_path, mode="r", bufsize=-1):
        """获取文件"""
        try:
            return self.sftp.file(file_path, mode=mode, bufsize=bufsize)
        except Exception as e:
            logger.error(f"获取文件失败:{e}")
            return False

    def open_file(self, file_path, mode="r", bufsize=-1):
        """打开文件"""
        try:
            return self.sftp.open(file_path, mode=mode, bufsize=bufsize)
        except Exception as e:
            logger.error(f"获取文件失败:{e}")
            return False

    def stat_path(self, file_path):
        """查看文件属性"""
        try:
            self.sftp.stat(file_path)
            return True
        except Exception as e:
            logger.error(f"文件不存在或stat失败:{e}")
            return False


# 测试linux类代码
if __name__ == '__main__':
    ip = "10.217.62.230"
    username = "wangbing3"
    port = 22
    password = "Kbne!!!222###90"
    local_path = "./har_analysis/ssh_linux.py"
    remote_path = "/home/sftp/hips_data/ssh_linux.py"

    host = SSHLinux(ip, username, password, port=port)
    host.connect()

    # host.send("pwd")
    res = host.send_invoke_shell_msg(password, "sudo ls /home/")
    # res = host.send_invoke_shell(password, "sudo ls /home/")
    res1 = [t.split() for t in res.split('\n')][1: -1]
    print(res1)
    # for t in res1:
    #     print(t.split())
    # host.upload_file(local_path, remote_path)
    # s = host.get_file(local_path)
    # print(s.read())
