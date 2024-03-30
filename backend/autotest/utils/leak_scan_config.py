#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2022/8/26 14:57  @Author: wangbing3  @Descript: 病毒库、漏洞库监控信息
import os.path
from pathlib import Path
from config import config

leak_infos = {
    'sdupbd.cab':
        {
            'name': 'sdupbd.cab',
            'intro': 'Windows病毒库',
            'url': 'https://sdup.qihucdn.com/lib/sdupbd.cab',
            'remind_day': 5,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("sdupbd")
        },
    'kplib.cab':
        {
            'name': 'kplib.cab',
            'intro': '鲲鹏病毒库',
            'url': 'http://dl.360safe.com/secdzqz/kplib.cab',
            'remind_day': 7,
            'download_path':  Path(config.DOWNLOAD_FILES_DIR).joinpath("kplib")
        },
    'bfup.ver.ini':
        {'name': 'bfup.ver.ini',
         'intro': 'Linux病毒库-1',
         'url': 'http://dl.360safe.com/secdzqz/4d5f197c-6a71-11ea-a48c-000c299b4503/bfup.ver.ini',
         'remind_day': 7,
         'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("bfup")
         },
    'bfupdate.ini':
        {
            'name': 'bfupdate.ini',
            'intro': 'Linux病毒库-2',
            'url': 'http://dl.360safe.com/secdzqz/4d5f197c-6a71-11ea-a48c-000c299b4503/bfupdate.ini',
            'remind_day': 10,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("bfupdate")

        },
    '360exthost.cab':
        {
            'name': '360exthost.cab',
            'intro': 'Winodws漏洞库',
            'url': 'https://dl.360safe.com/v3/360exthost.cab',
            'remind_day': 30,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("360exthost")
        },
    'qex.ini.cab':
        {
            'name': 'qex.ini.cab',
            'intro': 'Mac病毒库-1',
            'url': 'http://dl.360safe.com/secdzqz/mac/v3/viruslib/qex.ini.cab',
            'remind_day': 7,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("qex")
        },
    # 'safe_update.cab':
    #     {
    #         'name': 'safe_update.cab',
    #         'intro': 'Mac病毒库-2',
    #         'url': 'http://dl.360safe.com/secdzqz/mac/v3/viruslib/safe_update.cab',
    #         'remind_day': 7,
    #         'download_path': os.path.join(config.DOWNLOADS, "safe_update")
    #     },
    'win7shield.cab':
        {
            'name': 'win7shield.cab',
            'intro': 'Win7盾甲漏洞库',
            'url': 'https://dl.360safe.com/v3/win7shield.cab',
            'remind_day': 30,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("win7shield")
        },
    'offlinekits.cab':
        {
            'name': 'offlinekits.cab',
            'intro': '离线工具线上更新库',
            'url': 'http://dl.360safe.com/secdzqz/offlinekits.cab',
            'remind_day': 0,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("offlinekits")
        },
    'threatelistinfo.cab':
        {'name': 'threatelistinfo.cab',
         'intro': '威胁自查库更新',
         'url': 'http://dl.360safe.com/secdzqz/threate/threatelistinfo.cab',
         'remind_day': 0,
         'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("threatelistinfo")

         },
    'UpdateList.xml':
        {
            'name': 'UpdateList.xml',
            'intro': '漏洞库定期更新配置wsuscan',
            # 'url': 'http://dl.360safe.com/secdzqz/wsuscan/OSUpgrade/UpdateList.xml',
            # 'url': 'https://dl.360safe.com/secdzqz/wsuscan/Windows7/UpdateList.xml',
            'url': 'https://dl.360safe.com/secdzqz/wsuscan/Windows10/UpdateList.xml',
            'remind_day': 31,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("UpdateList")

        },
    "index.db":
        {
            'name': 'index.db',
            'intro': '软件库更新',
            'url': 'http://dl.360safe.com/secdzqz/software/index.db',
            'remind_day': 7,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("index_db")
        },
    "xc_bfupdate.ini":
        {
            'name': 'xc_bfupdate.ini',
            'intro': '信创漏洞库更新',
            'url': 'http://dl.360safe.com/secdzqz/xcpatch/bfupdate.ini',
            'remind_day': 0,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("xc_bfupdate")
        },
    "xc_bfupdate1.ini":
        {
            'name': 'xc_bfupdate1.ini',
            'intro': '信创漏洞库更新1',
            'url': 'http://dl.360safe.com/secdzqz/linuxpatch/bfupdate.ini',
            'remind_day': 0,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("xc_bfupdate1")
        },
    "ips_rule.cab":
        {
            'name': 'ips_rule.cab',
            'intro': 'IPS规则库',
            'url': 'http://dl.360safe.com/secdzqz/ips_rule/ips_rule.cab',
            'remind_day': 0,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("ips_rule")
        },
    "HotEvents.zip":
        {
            "name": "HotEvents.zip",
            "intro": "热点事件",
            "url": "http://dl.360safe.com/secdzqz/HotEvents.zip",
            "remind_day": 7,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("HotEvents")
        },
    "bfupvndt.ini":
        {
            "name": "bfupvndt.ini",
            "intro": "cwpp&linux漏洞库",
            "url": "http://dl.360safe.com/secdzqz/4d5f197c-6a71-11ea-a48c-000c299b4505/bfupvndt.ini",
            "remind_day": 10,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("bfupvndt")
        },
    "edr_cloud.xml.tar.gz":
        {
            "name": "edr_cloud.xml.tar.gz",
            "intro": "edr规则库",
            "url": "http://dl.360safe.com/secdzqz/edr_cloud/edr_cloud.xml.tar.gz",
            "remind_day": 10,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("edr_cloud")
        },
    "avlib_win1.zip":
        {
            "name": "avlib_win1.zip",
            "intro": "JD离线windows病毒库1",
            "url": "http://dl.360safe.com/secdzqz/jd/avlib_win1.zip",
            "remind_day": 10,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("avlib_win1")
        },
    "avlib_win2.zip":
        {
            "name": "avlib_win2.zip",
            "intro": "JD离线windows病毒库2",
            "url": "http://dl.360safe.com/secdzqz/jd/avlib_win2.zip",
            "remind_day": 10,
            'download_path': Path(config.DOWNLOAD_FILES_DIR).joinpath("avlib_win2")
        },
}

leak_info = {
    "sdupbd.cab": "Windows病毒库",
    "kplib.cab": "鲲鹏病毒库",
    "bfup.ver.ini": "Linux病毒库",
    "360exthost.cab": "Winodws漏洞库",
    "qex.ini.cab": "Mac病毒库",
    "safe_update.cab": "Mac病毒库",
    "win7shield.cab": "Win7盾甲漏洞库",
    "offlinekits.cab": "离线工具线上更新库",
    "threatelistinfo.cab": "威胁自查库",
    "UpdateList.xml": "漏洞库定期更新配置wsuscan",
    "bfupdate.ini": "Linux病毒库",
    "index.db": "软件库",
    "xc_bfupdate.ini": "信创漏洞库",
    "ips_rule.cab": "IPS规则库",
    "HotEvents.zip": "热点事件",
    "bfupvndt.ini": "cwpp&linux漏洞库",
    "edr_cloud.xml.tar.gz": "edr规则库",
    "avlib_win1.zip": "JD离线windows病毒库1",
    "avlib_win2.zip": "JD离线windows病毒库2"

}
