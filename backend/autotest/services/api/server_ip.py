import typing

from autotest.utils.response.codes import CodeEnum
from autotest.exceptions.exceptions import ParameterError
from autotest.models.api_models import ProjectInfo, ModuleInfo
from autotest.models.server_ip_models import ServerIpInfo
from autotest.schemas.api.serverip_query import ServerIpQuery, ServerIpId, ServerIpIn


class ServerIPService:
    @staticmethod
    async def list(params: ServerIpQuery) -> typing.Dict:
        """
        获取项目列表
        :param params:
        :return:
        """
        data = await ServerIpInfo.get_list(params)
        return data

    @staticmethod
    async def get_all() -> typing.Dict:
        """
        获取项目列表
        :return:
        """
        data = await ServerIpInfo.get_all()
        return data

    @staticmethod
    async def save_or_update(params: ServerIpIn) -> typing.Dict:
        """
        更新保存项目
        :param params:
        :return:
        """
        if params.id:
            server_info = await ServerIpInfo.get(params.id)
            if server_info.name != params.name:
                if await ServerIpInfo.get_server_by_name(params.name):
                    raise ParameterError(CodeEnum.PROJECT_NAME_EXIST)
        else:
            if await ServerIpInfo.get_server_by_name(params.name):
                raise ParameterError(CodeEnum.PROJECT_NAME_EXIST)

        return await ServerIpInfo.create_or_update(params.dict())

    @staticmethod
    async def deleted(params: ServerIpId) -> int:
        """
        删除服务器ip  admin可删除其他， 其他用户只能删除自己创建
        :param params:
        :return:
        """
        return await ServerIpInfo.delete(params.id)

