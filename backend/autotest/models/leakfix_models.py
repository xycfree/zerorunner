#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024/1/23 11:11 __walter__ @Desc:

from sqlalchemy import Integer, String, Text, DateTime, BigInteger, func, \
    distinct, text, and_, JSON, DECIMAL, select, update, Boolean, case, Float
from sqlalchemy.orm import aliased, mapped_column

from autotest.models.base import Base
from autotest.models.system_models import User
from autotest.schemas.api.leaks_query import LeakfixQuery


class LeakfixInfo(Base):
    """病毒漏洞库信息"""
    __tablename__ = 'leakfix_info'

    url = mapped_column(String(255),  comment='漏洞病毒库url', index=True, nullable=False)
    name = mapped_column(String(64), nullable=True, comment='项目名称')
    addr = mapped_column(String(255), nullable=False, comment='文件下载路径')
    size = mapped_column(Integer, nullable=True, comment='文件大小')
    md5 = mapped_column(String(64), nullable=False, comment='文件MD5')
    c_time = mapped_column(DateTime, nullable=False, comment="病毒漏洞库创建时间")
    remark = mapped_column(String(128), nullable=True, comment="备注")

    @classmethod
    async def get_list(cls, params: LeakfixQuery):
        q = [cls.enabled_flag == 1]

        if params.name:
            q.append(cls.name.like('%{}%'.format(params.name)))
        if params.created_by_name:
            q.append(User.nickname.like('%{}%'.format(params.created_by_name)))
        if params.id:
            q.append(cls.id == params.id)
        if params.ids:
            q.append(cls.id.in_(params.ids))

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
    async def get_leakfix_by_id(cls, id: int):
        stmt = select(cls.get_table_columns()).where(cls.id == id, cls.enabled_flag == 1)
        return await cls.get_result(stmt)

    @classmethod
    def get_leakfix_id_list(cls):
        # with_entities()可以添加或删除（简单地说：替换）模型或列；您甚至可以使用它来修改查询，用您自己的函数替换选定的实体  通过该方法指定结果要返回的列
        return cls.query.filter(cls.enabled_flag == 1).with_entities(
            cls.id, cls.name, cls.url, cls.addr, cls.c_time, cls.size, cls.md5).all()

    @classmethod
    async def get_leakfix_by_name(cls, name, orderby=True):
        """
        :param name: 检索名称
        :param orderby: True: 按id倒序排序
        :return:
        """
        stmt = select(cls.id).where(cls.name == name, cls.enabled_flag == 1).order_by(
            cls.id.desc() if orderby else cls.id.desc())
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_leakfix_by_names(cls, name):
        stmt = select(cls.get_table_columns()).where(cls.name == name, cls.enabled_flag == 1)
        return await cls.pagination(stmt)


    @classmethod
    def get_all_count(cls):
        return cls.query.filter(cls.enabled_flag == 1).count()

    @classmethod
    def get_leakfix_ids(cls):
        return cls.query.filter(cls.enabled_flag == 1).with_entities(cls.id).all()