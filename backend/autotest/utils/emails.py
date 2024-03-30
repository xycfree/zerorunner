#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2020/3/8 12:15  @Author: xycfree  @Descript:

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from datetime import datetime
from autotest.init import logger

from autotest.utils.leak_scan_config import leak_infos
from config import config


def send_email(info, now_time, remark=""):
    """ 发送邮件
    :param info:
    :param remark:
    :param now_time:
    :return:
    """
    if config.DEBUG:  # debug为True 说明是测试本地或开发环境
        receives = ["wangbing3@360.cn"]
    else:
        receives = ["wangbing3@360.cn", "chenjia1@360.cn", "wuxia@360.cn", "xuke@360.cn"]

    cc_receiver = []  # 抄送 "g-qc-EPP@360.cn"

    try:
        _tr = '<tr style="color: {};">{}</tr>'
        _td = "<td>{}</td>"
        trs = ""

        win7shield = [t for t in info if t.get("name") in ["win7shield.cab"]][0]
        exthost = [t for t in info if t.get("name") in ["360exthost.cab"]][0]

        try:
            ss = datetime.strptime(win7shield.get("last_time"), "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                exthost.get("last_time"), "%Y-%m-%d %H:%M:%S")
            logger.info(f"win7shield - 360exthost= {ss}")
            ss = ss.days + 1 if ss.seconds / 3600 > 0.5 else ss.days
            if ss > 2:
                green = True
            else:
                green = False
            logger.info(f"greep:{green}")
        except Exception as e:
            logger.warning(e)
            green = False

        for idx, i in enumerate(info):
            _name = i.get("name", "")
            _days = i.get("days", 0)
            _status = i.get("status", 1)  # 0:异常  1: 正常
            # logger.info(f"邮件发送，遍历数据，name:{_name}, days:{_days}, status: {_status}.")
            if _days == "":
                logger.warning(f"数据name: {_name}, days异常:{_days}, 重置为0!")
                _days = 0
            if _status:
                if _name in ["win7shield.cab", "360exthost.cab"] and green:
                    style = "green"
                elif _name in leak_infos.keys() and _days > leak_infos[_name]['remind_day'] != 0:
                    style = "red"
                else:
                    style = "blank"
            else:
                style = "gray"

            tds = "\n".join([
                _td.format(idx+1), _td.format(leak_infos[i.get("name", "")]['intro']),
                _td.format(i.get("name", "")), _td.format(i.get("md5", "")),
                _td.format(i.get("days", "")), _td.format(i.get("last_time", "")),
                _td.format(i.get("current_time", "")), _td.format(i.get("url", "")),
                _td.format(i.get("remark", ""))])
            trs += _tr.format(style, tds)

        mail_msg = """
            <html>
                <head></head>
                <body>
                    <div style="color: blank;">
                        <h3>漏洞库&病毒库更新结果</h3>
                            
                            <p> {} </p>
                                <table border="1" style="color: blank;">
                                    <tr> 
                                        <th>序号</th>
                                        <th>名称</th>
                                        <th>文件名</th>
                                        <th>MD5</th>
                                        <th>更新天数</th>
                                        <th>最新更新时间</th>
                                        <th>当前时间</th>
                                        <th>文件地址</th>
                                        <th>备注</th>
                                        </tr> {}
                                </table>
                        </div>
                    </body>
            </html>
        """.format(remark, trs)
        return smtp_email(config.MAIL_SENDER, receives + cc_receiver, mail_msg, cc_receiver, now_time)
    except smtplib.SMTPException as e:
        logger.error('Email send error: {}, {}'.format(str(e), now_time))
        return False


def smtp_email(sender, receives, mail_msg, cc_receiver, now_time=""):
    """ 邮件发送
    :param cc_receiver:
    :param now_time:
    :param sender: 发件人
    :param receives: 收件人+抄送人
    :param mail_msg: 邮件内容
    :return:
    """

    # 传入邮件发送者、接受者、抄送者邮箱以及主题
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = sender
    message['To'] = ','.join(receives)
    message['Cc'] = ";".join(cc_receiver)
    message['Subject'] = Header("漏洞库&病毒库更新状态", "utf-8")

    send_times = 3

    # 登入邮箱发送邮件
    server = smtplib.SMTP(config.MAIL_HOST, port=config.MAIL_PORT, timeout=3000)  # 端口默认是25,所以不用指定, 超时默认300s
    # server.set_debuglevel(1)
    try:
        server.login(config.MAIL_USER, config.MAIL_PASS)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Email Authentication failed: {str(e)}")
        return False
    while send_times:
        try:
            server.sendmail(sender, receives + cc_receiver, message.as_string())  # 收件人和抄送人一起发送
            logger.info('Email send success!, {}'.format(now_time))
            return True
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"收件人查找失败: {str(e)}，times: {send_times}")
            send_times -= 1
            continue
        except Exception as e:
            logger.error(f"Email send failed!: {str(e)}")
            return False
        finally:
            # 不退出则可以避免smtplib.SMTPServerDisconnected: please run connect() first错误，未尝试
            server.quit()
    logger.error("收件人查询失败，本次邮件发送失败!")
    return False


if __name__ == '__main__':
    receives = ["wangbing3@360.cn"]
    mail_msg = "hello world"
    s = smtp_email(config.MAIL_SENDER, receives, mail_msg, [])
    print(s)
