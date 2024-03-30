#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024/1/17 15:59 __walter__ @Desc: hulk服务器信息

import typing

from sqlalchemy import Integer, String, Text, DateTime, BigInteger, func, \
    distinct, text, and_, JSON, DECIMAL, select, update, Boolean, case, Float
from sqlalchemy.orm import aliased, mapped_column

from autotest.models.base import Base
from autotest.models.system_models import User
from autotest.schemas.api.serverip_query import ServerIpQuery

from loguru import logger


class ServerIpInfo(Base):
    """服务器-管控版本信息"""
    __tablename__ = 'server_ver'

    ip = mapped_column(String(32), unique=True, comment='服务器IP', index=True, nullable=False)
    name = mapped_column(String(64), nullable=False, comment='项目名称')

    system_type = mapped_column(Integer, default=0, nullable=True,
                                comment="服务器操作系统, 0:未知 1:linux[centos, redhat] 2:ubuntu 3:mac 4:windows")
    server_source = mapped_column(String(32), default=None, comment="服务器来源, hulk, ops")
    cpu = mapped_column(Integer, default=0, comment='CPU数量')
    mem = mapped_column(Integer, default=0, comment="内存/G")
    disk_total = mapped_column(Float, default=0.0, comment="磁盘空间/G")
    disk_use = mapped_column(Float, default=0.0, comment="磁盘使用量/G")
    is_install = mapped_column(Integer, default=0, comment="是否安装epp, 0:未知  1:未安装 2:已安装")
    is_run = mapped_column(Integer, default=0, comment="是否运行epp，0:未知 1:未运行 2:运行")
    is_multi = mapped_column(Integer, default=0, comment="是否存在上下级关系 0:未知 1:仅本级 2:有且上级 4:有且下级")
    epp_version = mapped_column(String(32), default=None, comment="epp版本")
    server_type = mapped_column(String(32), default=None, comment="服务器性质, 开发/测试")
    server_users = mapped_column(String(1024), comment="服务器用户权限")
    remark = mapped_column(String(1024), comment="备注")

    @classmethod
    async def get_list(cls, params: ServerIpQuery):
        q = [cls.enabled_flag == 1]

        if params.name:
            q.append(cls.name.like('%{}%'.format(params.name)))
        if params.created_by_name:
            q.append(User.nickname.like('%{}%'.format(params.created_by_name)))
        if params.id:
            q.append(cls.id == params.id)
        if params.ids:
            q.append(cls.id.in_(params.ids))
        if params.ip:
            q.append(cls.ip.like(f'%{params.ip}%'))
        if params.epp_version:
            q.append(cls.epp_version.like(f'%{params.epp_version}%'))

        # logger.info(f"q: {q[0]}, {q[1]}")  # q: project_info.enabled_flag = :enabled_flag_1, project_info.name LIKE :name_1
        u = aliased(User)  # 申明表别名
        stmt = select(cls.get_table_columns(),
                      u.nickname.label('updated_by_name'),  # 通过别名增加字段
                      User.nickname.label('created_by_name')) \
            .where(*q) \
            .outerjoin(u, u.id == cls.updated_by) \
            .outerjoin(User, User.id == cls.created_by) \
            .order_by(cls.id.desc())
        return await cls.pagination(stmt)

    @classmethod
    async def get_server_by_id(cls, id: int):
        stmt = select(cls.get_table_columns()).where(cls.id == id, cls.enabled_flag == 1)
        return await cls.get_result(stmt)

    @classmethod
    def get_server_id_list(cls):
        # with_entities()可以添加或删除（简单地说：替换）模型或列；您甚至可以使用它来修改查询，用您自己的函数替换选定的实体  通过该方法指定结果要返回的列
        return cls.query.filter(cls.enabled_flag == 1) \
            .with_entities(cls.id,
                           cls.ip,
                           cls.name,
                           cls.epp_version,
                           cls.is_install,
                           cls.is_run,
                           cls.is_multi
                           ).all()

    @classmethod
    async def get_server_by_name(cls, name):
        stmt = select(cls.id).where(cls.name == name, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    def get_all_count(cls):
        return cls.query.filter(cls.enabled_flag == 1).count()

    @classmethod
    def get_server_ids(cls):
        return cls.query.filter(cls.enabled_flag == 1).with_entities(cls.id).all()
