import copy
import os
import typing
from pathlib import Path

from loguru import logger
from starlette import status
from starlette.responses import FileResponse, HTMLResponse

from autotest.utils.response.codes import CodeEnum
from autotest.exceptions.exceptions import ParameterError
from autotest.models.api_models import ModuleInfo
from autotest.models.leakfix_models import LeakfixInfo
from autotest.schemas.api.leaks_query import LeakfixQuery, LeakfixIn, LeakfixId
from config import config


class LeakfixService:


    @staticmethod
    async def list(params: LeakfixQuery) -> typing.Dict:
        """
        获取项目列表
        :param params:
        :return:
        """
        data = await LeakfixInfo.get_list(params)
        # logger.debug(data)
        # _data = copy.deepcopy(data)
        # _li = []
        # for t in _data['rows']:
        #     t['addr'] = Path(config.DOWNLOAD_FILES_DIR).joinpath(t['addr'])
        #     _li.append(t)
        # data['rows'] = _li

        return data

    @staticmethod
    async def get_all() -> typing.Dict:
        """
        获取项目列表
        :return:
        """
        data = await LeakfixInfo.get_all()
        return data

    @staticmethod
    async def get_leakfix_by_name(name: str) -> typing.Dict:
        """
        获取项目列表
        :return:
        """
        data = await LeakfixInfo.get_leakfix_by_name(name)
        return data



    @staticmethod
    async def history_list(params: LeakfixQuery) -> typing.Dict:
        """
        获取项目列表
        :param params:
        :return:
        """
        data = await LeakfixInfo.get_leakfix_by_names(params.name)
        return data


    @staticmethod
    async def save_or_update(params: LeakfixIn) -> typing.Dict:
        """
        更新保存项目
        :param params:
        :return:
        """
        if params.id:
            server_info = await LeakfixInfo.get(params.id)
            if server_info.name != params.name:
                if await LeakfixInfo.get_server_by_name(params.name):
                    raise ParameterError(CodeEnum.PROJECT_NAME_EXIST)
        else:
            if await LeakfixInfo.get_server_by_name(params.name):
                raise ParameterError(CodeEnum.PROJECT_NAME_EXIST)

        return await LeakfixInfo.create_or_update(params.dict())

    @staticmethod
    async def deleted(params: LeakfixId) -> int:
        """
        删除服务器ip  admin可删除其他， 其他用户只能删除自己创建
        :param params:
        :return:
        """
        return await LeakfixInfo.delete(params.id)

    @staticmethod
    async def download(file_id: str) -> typing.Union[FileResponse, HTMLResponse]:
        file_info = await LeakfixInfo.get(file_id)
        if not file_info:
            logger.error(f'{file_id} 文件不存在！')
            return HTMLResponse(content="文件不存在")
        file_dir = Path(config.DOWNLOAD_FILES_DIR).joinpath(file_info.addr).as_posix()
        # if not os.path.isfile(file_dir):
        if not Path(file_dir).is_file():
            logger.error(f'{file_info.name}文件不存在！')
            return HTMLResponse(content="文件不存在")

        return FileResponse(
            path=file_dir,
            filename=file_info.name,
            headers={
                "Content-Type": "application/octet-stream",
                "Access-Control-Expose-Headers": "Content-Disposition",
                "content-disposition": f"attachment;filename={file_info.name}"
            })
