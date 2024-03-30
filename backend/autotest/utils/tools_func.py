#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/9/22 10:56  @Author: xycfree  @Descript:
"""

"""

import datetime
import decimal
import json
from typing import Union

from autotest.models import Base


def _alchemy_encoder(obj):
    """
    处理序列化中的时间和小数
    :param obj:
    :return:
    """
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


def serialize_sqlalchemy_obj(obj) -> Union[dict, list]:
    """
    序列化fetchall()后的sqlalchemy对象
    https://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/
    :param obj:
    :return:
    """
    if isinstance(obj, list):
        # 转换fetchall()的结果集
        return json.loads(json.dumps([dict(r) for r in obj], default=_alchemy_encoder))
    else:
        # 转换fetchone()后的对象
        return json.loads(json.dumps(dict(obj), default=_alchemy_encoder))


class TypeCast:

    def to_dict(self):  # 方法一，该方法直接获取数据库原始数值,对于一些特殊字符如时间戳无法转换
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}  # 记得加None(网上一些教程没有加None是无法使用的)

    Base.to_dict = to_dict  # 如果使用的是flask-sqlalchemy，就使用对应的基类

    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    # def to_dict(self):  # 方法二定制，将时间戳值转为str类型，其他直接输出
    # result = {}
    # for key in self.__mapper__.c.keys():
    #     if type(getattr(self, key)) == datetime.datetime:
    #         result[key] = str(getattr(self, key))
    #     else:
    #         result[key] = getattr(self, key)
    # return result

    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
