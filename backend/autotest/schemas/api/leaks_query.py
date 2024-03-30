import typing
from pydantic import Field, BaseModel
from pydantic.schema import datetime

from autotest.schemas.base import BaseSchema


class LeakfixIn(BaseModel):
    id: int = Field(None, description="id")
    name: str = Field(..., description="项目名称")
    c_time: datetime = Field(None, description="更新时间")
    url: str = Field(..., description="url")
    addr: str = Field(..., description="下载地址")
    md5: str = Field(..., description="文件MD5")
    size: str = Field(..., description="文件大小")
    remark: str = Field(None, description="备注")


class LeakfixQuery(BaseSchema):
    """查询参数序列化"""

    id: int = Field(None, description="id")
    ids: typing.List = Field(None, description="id 列表")
    name: str = Field(None, description="项目名称")
    order_field: str = Field(None, description="排序字段")
    sort_type: str = Field(None, description="排序类型")
    created_by_name: str = Field(None, description="创建人名称")


class LeakfixId(BaseSchema):
    """删除"""

    id: int = Field(..., description="id")
