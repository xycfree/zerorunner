#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2022/10/1 17:17  @Author: wangbing3  @Descript: 服务器版本操作
from loguru import logger

from autotest.utils.ssh_linux import SSHLinux
from autotest.utils.utils import disk_unit_conversion


class ServerInfo(SSHLinux):

    def get_cpu_info(self):
        cmd = "cat /proc/cpuinfo | grep processor | wc -l"
        flag, std_out = self.send(cmd)
        if flag:
            logger.info(f"[ssh] 服务器: {self.host},获取cpu: {std_out}")
            return flag, std_out
        logger.error(f"[ssh] 服务器: {self.host},获取cpu失败: {std_out}")
        return flag, 0

    def get_free_info(self):
        cmd = """ cat /proc/meminfo | grep 'MemTotal' | awk '{print $2 / 1024}' | sed "s/\..*//g" """  # free -h 有的服务器没有-h的单位
        try:
            flag, std_out = self.send(cmd)
            if flag:
                return flag, round(float(std_out) / 1024, 2)
                # cmd = "free"
                # flag, std_out = self.send(cmd)
                # logger.info(f"[ssh] 服务器: {self.host},获取内存: {std_out}")
                # return flag, round(float(std_out.split()[7])/1024/1024, 2)   # 16G
            logger.error(f"[ssh] 服务器: {self.host},获取内存失败: {std_out}")
            return flag, 0
        except Exception as e:
            logger.error(f"[ssh] 服务器: {self.host},获取内存失败: {str(e)}")
            return False, 0

    def get_disk_info(self, try_flag: bool = False):
        """ 获取服务器磁盘信息
        :param try_flag: 初次为FALSE， 如果不存在/data目录，会尝试创建，然后再次回调进行获取
        :return:
        """
        cmd = "df -h /data"
        #  df /data/ -m | grep / | awk '{print $2 / 1024}' | sed "s/\..*//g"  # 获取总的磁盘量
        #  df /data/ -m | grep / | awk '{print $3 / 1024}' | sed "s/\..*//g"  # 获取已使用的磁盘量

        flag, std_out = self.send(cmd)
        """
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/sda1       400G   84G  317G  21% /
        True Siz Use
        """
        try:
            if flag:
                logger.info(f"[ssh] 服务器:{self.host},获取磁盘信息: {std_out.split()}")
                total, use = std_out.split()[8], std_out.split()[9]  # M G T
                total = disk_unit_conversion(total)
                use = disk_unit_conversion(use)
                logger.debug(f"[ssh] 服务器:{self.host},磁盘信息转换:{flag}, {total}, {use}")
                return flag, total, use
            logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息失败: {std_out}")
            return flag, 0, 0
        except Exception as e:
            logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息异常:{str(e)}")
            if "No such file or directory" in std_out and not try_flag:
                logger.info(f"[ssh] 服务器:{self.host},没有/data目录，尝试创建，并再次获取信息")
                cmd_mkdir = "sudo  mkdir /data"
                self.send_invoke_shell(self.password, cmd_mkdir)
                return self.get_disk_info(try_flag=True)
            else:
                logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息失败: {std_out}")
                return flag, 0, 0

    def get_user_info(self):
        cmd = "sudo cat /etc/passwd | head -100 | cut -f1 -d:"
        flag, std_out = self.send_invoke_shell(self.password, cmd)
        if not flag:
            logger.info(f"[ssh] 服务器:{self.host},获取用户信息失败")
            return []
        users = [t.strip() for t in std_out.split("\n")][2:-1]
        excludes = ['root', 'bin', 'daemon', 'adm', 'lp', 'sync', 'shutdown', 'halt', 'mail', 'operator', 'games',
                    'ftp', 'nobody', 'systemd-network', 'dbus', 'polkitd', 'postfix', 'chrony', 'sshd', 'ntp',
                    'logsget', 'puppet', 'tcpdump', 'syncops', '360sec', 'sysadmin', 'xitong', 'infra',
                    'jinxin', 'lihuasha', 'weidong', 'wangbaoping', 'lixiaoxiao', 'zhangzetao', 'linjiyang',
                    'weijianjun', 'sunyunfeng', 'gaoyunguang', 'liuyi3', 'fenglu1', 'jingjianhua',
                    'wangguo', 'yangxu5',
                    ]
        return list(set(users).difference(set(excludes)))  # 列表求并集， 获取用户权限

    def get_epp_install(self) -> dict:
        """ 获取epp安装状态
        :return: 1: 未安装  2: 已安装  0: 未知
        """

        cmd = "sudo docker ps"
        logger.info(f"服务器:{self.host}, 获取epp安装状态,命令: {cmd}")
        flag, std_out = self.send_invoke_shell(self.password, cmd)
        logger.debug(f"get_epp_install: {std_out}")
        if not flag:
            logger.info(f"获取服务器:{self.host}epp是否安装状态失败: {std_out}")
            return {"status": 0, "msg": std_out}

        # logger.debug(f"std_out: \n{std_out}")
        if "cactus-web" in std_out:
            return {"status": 2, "msg": "已安装"}
        return {"status": 1, "msg": "未安装"}
        # 未安装内容含有：no such file or directory
        # if "no such file or directory" in std_out:

    def get_epp_run(self) -> dict:
        """ 获取epp是否运行
        :return: 1: 未运行  2: 运行中  0: 未知
        """
        cmd = "sudo docker-compose -f /home/s/lcsd/docker-compose.yml ps"
        flag, std_out = self.send_invoke_shell(self.password, cmd)
        if not flag:
            logger.info(f"获取服务器:{self.host}epp是否运行失败: {std_out}")
            return {"status": 0, "msg": std_out}

        logger.debug(f"std_out: \n{std_out}")
        """
            docker-compose -f /home/s/lcsd/docker-compose.yml ps
            NAME                    COMMAND                  SERVICE                 STATUS              PORTS
            cactus-cascade          "/bin/sh -c '/bin/sh…"   cactus-cascade          running             0.0.0.0:36093->36093/tcp, :::36093->36093/tcp
            cactus-fdfs             "/etc/fdfs/start.sh"     cactus-fdfs             running             32122/tcp, 33000/tcp
            cactus-newtransserver   "/bin/newtransserver"    cactus-newtransserver   running             0.0.0.0:8090->8080/tcp, :::8090->8080/tcp
            cactus-nginx            "/start.sh"              cactus-nginx            running             0.0.0.0:443->443/tcp, :::443->443/tcp, 0.0.0.0:8082->8082/tcp, :::8082->8082/tcp, 0.0.0.0:8081->80/tcp, :::8081->80/tcp
            cactus-security         "/bin/sh -c '/bin/sh…"   cactus-security         running             
            cactus-web              "/bin/sh -c '/bin/sh…"   cactus-web              running             0.0.0.0:8022->22/tcp, :::8022->22/tcp
            lcsd-lcs-1              "/bin/bash -c 'sh /h…"   lcs                     running             0.0.0.0:80->80/tcp, :::80->80/tcp
            lcsd-nginx-1            "/docker-entrypoint.…"   nginx                   running             80/tcp, 0.0.0.0:8080->8080/tcp, :::8080->8080/tcp
            lcsd-nsqd-1             "/bin/sh -c /docker-…"   nsqd                    running             
            lcsd-nsqlookupd-1       "/bin/sh -c /docker-…"   nsqlookupd              running             
            lcsd-p2p-1              "/bin/bash -c 'sh /u…"   p2p                     running             0.0.0.0:81->81/udp, :::81->81/udp
            lcsd-redis_serv-1       "redis-server /usr/l…"   redis_serv              running             6379/tcp
            log_audit               "/usr/local/bin/vect…"   cactus_log_audit        restarting          
            mongodb                 "docker-entrypoint.s…"   cactus-mongo            running             27017/tcp
            mysql                   "docker-entrypoint.s…"   cactus-mysql            running             3306/tcp, 33060/tcp
            naceng                  "/etc/init.d/gscrun.…"   cactus-naceng           running             0.0.0.0:22315->22315/tcp, :::22315->22315/tcp
            redis                   "redis-server /usr/l…"   cactus-redis            running             6379/tcp
            seccscan                "/bin/sh -c '/bin/sh…"   cactus-seccscan         running             
            [root@p49915v wangbing3]# 
        """
        if "cactus-web" in std_out:
            resu = {"status": 2, "msg": "运行中"}
        else:
            resu = {"status": 1, "msg": "未运行"}
        logger.info(f"获取服务器:{self.host},epp运行状态: {resu}")
        return resu

    def get_epp_version(self):
        cmd = "cat /data/docker/cactus-web/system/safe-cactus/version"
        """
            p=newtianqin
            sv=10.0.0.06108
            v=10.0.0.06108
            fv=10.0.0.06108
            b=develop-10.0.0.06108
            r=94300ddabba9cd6fc576e8d20a2be78c6ec9de17
            d=20221022184205
            u=-t
        """
        flag, std_out = self.send(cmd)
        logger.debug(f"std_out: \n{std_out}")
        if flag and "p=newtianqin" in std_out:
            logger.info(f'服务器IP:{self.host}, 安装epp服务，版本信息: {std_out.split()[1].split("=")[1]}')
            return flag, std_out.split()[1].split("=")[1]
        logger.info(f"该环境:{self.host}没有安装epp!")
        return flag, ""

    def get_epp_multi(self):
        """ 获取epp是否存在多级
        :return: 0: 未知， 1:仅本级  2：有且上级  4：有且下级
        """
        multi_info = {
            "0": "未知",
            "1": "仅本级",
            "2": "包含下级",
            "4": "为下级"
        }
        global resu
        cmd = 'sudo docker exec -it mysql sh -c \'exec mysql -p"$MYSQL_ROOT_PASSWORD" -e "select id,address,guid,parent_guid from cactus.center \G;"\''
        flag, std_out = self.send_invoke_shell(self.password, cmd)
        if not flag:
            logger.info(f"获取服务器:{self.host}epp级联状态失败: {std_out}")
            return {"status": 0, "msg": multi_info["0"]}, []
        std_out = std_out.split('\n')[4:-1]
        logger.debug(f"std_out: \n{std_out}")
        li = []
        di = {}
        for i in std_out:
            if "row ******" in i.strip() and di:
                li.append(di)
                di = {}
                continue
            try:
                k, v = i.strip().split(": ")
            except ValueError:
                k, v = i.strip().split(": ")[0], ""
            di[k] = v
        li.append(di)

        logger.debug(f"center表数据: {li}")

        li_len = len(li)  # center表数据量
        if li_len == 0:
            logger.info(f"获取服务器:{self.host},获取epp级联状态：未知!")
            return {"status": 0, "msg": multi_info["0"]}, li
        elif li_len == 1:
            logger.info(f"获取服务器:{self.host},获取epp级联状态：仅本级!")
            return {"status": 1, "msg": multi_info["1"]}, li
        else:
            for i in li:
                if i.get("address") == self.host:
                    if not i.get("parent_guid"):
                        resu = {"status": 2, "msg": multi_info["2"]}
                    else:
                        resu = {"status": 4, "msg": multi_info["4"]}
            logger.info(f"获取服务器:{self.host},获取epp级联状态: {resu}")
            return resu, li


class XCServerInfo(ServerInfo):
    """信创平台服务器资源获取"""

    def get_disk_info(self, try_flag: bool = False):
        cmd = "df -h /opt"
        #  df /data/ -m | grep / | awk '{print $2 / 1024}' | sed "s/\..*//g"  # 获取总的磁盘量
        #  df /data/ -m | grep / | awk '{print $3 / 1024}' | sed "s/\..*//g"  # 获取已使用的磁盘量

        flag, std_out = self.send(cmd)
        """
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/sda1       400G   84G  317G  21% /
        True Siz Use
        """
        try:
            if flag:
                logger.info(f"[ssh] 服务器:{self.host},获取磁盘信息: {std_out.split()}")
                total, use = std_out.split()[8], std_out.split()[9]  # M G T
                total = disk_unit_conversion(total)
                use = disk_unit_conversion(use)
                logger.debug(f"[ssh] 服务器:{self.host},磁盘信息转换:{flag}, {total}, {use}")
                return flag, total, use
            logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息失败: {std_out}")
            return flag, 0, 0
        except Exception as e:
            logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息异常:{str(e)}")
            if "No such file or directory" in std_out and not try_flag:
                logger.info(f"[ssh] 服务器:{self.host},没有/opt目录，尝试创建，并再次获取信息")
                cmd_mkdir = "sudo  mkdir /opt"
                self.send_invoke_shell(self.password, cmd_mkdir)
                return self.get_disk_info(try_flag=True)
            else:
                logger.error(f"[ssh] 服务器:{self.host},获取磁盘信息失败: {std_out}")
                return flag, 0, 0

    def get_epp_version(self):
        cmd = "cat /opt/360/eppmc/conf/sdup.ini"
        """
            [EPP_MC]
            Ver=10.0.0.2319
            SystemName=nfs
            Arch=x86_64
            PackageName=360eppmc-10.0.0.2319-nfs.x86_64.rpm
            MD5=1f92e8b6a8c525cb2ef47be4ed06e72c
            [INFO]
            修复问题：
            1、去掉nginx；
            2、升级jdk；
            3、tomcat禁用put。
        """
        flag, std_out = self.send(cmd)
        logger.debug(f"std_out: \n{std_out}")
        if flag and "EPP_MC" in std_out:
            logger.info(f'服务器IP:{self.host}, 安装XC管控服务，版本信息: {std_out.split()[1].split("=")[1]}')
            return flag, std_out.split()[1].split("=")[1]
        logger.info(f"该环境:{self.host}没有安装管控!")
        return flag, ""


    def get_epp_install(self) -> dict:
        # cmd = "ps -ef | grep eppmc | wc -l"
        cmd = "systemctl status eppmc"
        logger.info(f"服务器:{self.host}, 获取epp安装状态,命令: {cmd}")
        flag, std_out = self.send(cmd)
        logger.debug(f"get_epp_install: {std_out}")
        if not flag:
            logger.info(f"获取服务器:{self.host} XC是否安装状态失败: {std_out}")
            return {"status": 0, "msg": std_out}

        # logger.debug(f"std_out: \n{std_out}")
        if int(std_out) > 1:
            return {"status": 2, "msg": "已安装"}
        return {"status": 1, "msg": "未安装"}
        # 未安装内容含有：no such file or directory
        # if "no such file or directory" in std_out:

    def get_epp_run(self) -> dict:
        pass

    def get_epp_multi(self):
        pass





if __name__ == '__main__':
    host = '10.220.185.104'
    from config import config
    user = ServerInfo(host, config.SERVER_USER, config.SERVER_PASS)
    conn_status = user.connect()
    if not conn_status:
        print('连接失败！')
        exit()

    # flag, res = user.get_cpu_info()
    # print(flag, res)

    flag, res = user.get_free_info()
    print(flag, res)

    flag, total, use = user.get_disk_info()
    print(flag, total, use)

    # flag, res = user.get_epp_version()
    # print(f"服务器版本:{flag}, {res}")

    # res = user.get_epp_install()
    # print(f"get_epp_install: {res}")
    #
    # res, li = user.get_epp_multi()
    # print(res, li)
    #
    # res = user.get_epp_run()
    # print(res)
    #
    # res = user.get_user_info()
    # print(res)

# CPU个数
# cat /proc/cpuinfo | grep processor | wc -l

# 内存信息
#  cat /proc/meminfo

# 磁盘 data目录空间
# df -h /data


# 项目运行状态
# docker-compose -f /home/s/lcsd/docker-compose.yml  ps

# 项目版本
#  cat /data/docker/cactus-web/system/safe-cactus/version

# 服务器用户
# sudo cat /etc/sudoers

"""
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host,22,'user','PWD')
    std_in,std_out,std_err = ssh_client.exec_command('cd /home/swuser/share/;tar -zxvf requests-2.13.0.tar.gz;cd requests-2.13.0;sudo -S python setup.py install',get_pty=True)  #在command命令最后加上 get_pty=True，执行多条命令 的话用；隔开，另外所有命令都在一个大的单引号范围内引用
    std_in.write('PWD'+'\n') #执行输入命令，输入sudo命令的密码，会自动执行
    for line in std_out:
        print line.strip('\n')
    ssh_client.close()
except Exception,e:
    print e

"""
