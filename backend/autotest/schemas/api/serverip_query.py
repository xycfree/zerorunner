import typing

from pydantic import Field, BaseModel

from autotest.schemas.base import BaseSchema


class ServerIpIn(BaseModel):

    id: int = Field(None, description="id")
    name: str = Field(None, description="项目名称")
    ip: str = Field(..., description="服务器IP")
    system_type: str = Field(None, description="服务器操作系统")
    server_source: str = Field(None, description="服务器来源")
    cpu: str = Field(None, description="CPU数量")
    mem: str = Field(None, description="内存/G")
    disk_total: str = Field(None, description="磁盘空间/G")
    disk_use: str = Field(None, description="磁盘使用量/G")
    is_install: str = Field(None, description="是否安装epp")
    is_run: str = Field(None, description="是否运行epp")
    is_multi: str = Field(None, description="是否存在上下级关系")
    epp_version: str = Field(None, description="epp版本")
    server_type: str = Field(None, description="服务器性质")
    server_users: str = Field(None, description="服务器用户权限")
    remark: str = Field(None, description="备注")


class ServerIpQuery(BaseSchema):
    """查询参数序列化"""

    id: int = Field(None, description="id")
    ids: typing.List = Field(None, description="id 列表")
    name: str = Field(None, description="项目名称")
    ip: str = Field(None, description="ip")
    epp_version: str = Field(None, description="epp版本")
    order_field: str = Field(None, description="排序字段")
    sort_type: str = Field(None, description="排序类型")
    created_by_name: str = Field(None, description="创建人名称")


class ServerIpId(BaseSchema):
    """删除"""

    id: int = Field(..., description="id")
