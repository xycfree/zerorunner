import requests
from fastapi import APIRouter, Depends

from autotest.utils.local import g
from autotest.utils.response.codes import CodeEnum
from autotest.utils.response.http_response import partner_success
from autotest.schemas.api.serverip_query import ServerIpQuery, ServerIpIn, ServerIpId
from autotest.schemas.api.leaks_query import LeakfixQuery, LeakfixId, LeakfixIn
from autotest.services.api.leakfix import LeakfixService
from autotest.services.system.user import UserService, permission_required, user_auth_verify
from loguru import logger

router = APIRouter()


@router.post('/list', description="病毒漏洞库列表")
async def server_list(params: LeakfixQuery):
    logger.debug(f"project list params: {params}, request data: {await g.request.json()}")
    data = await LeakfixService.list(params)
    return partner_success(data)


@router.post('/history/list', description="病毒漏洞库历史")
async def server_list(params: LeakfixQuery):
    logger.debug(f"project list params: {params}, request data: {await g.request.json()}")
    data = await LeakfixService.history_list(params)
    return partner_success(data)



@router.post('/getAllLeaks', description="获取所有服务器信息")
async def get_all_serverip():
    data = await LeakfixService.get_all()
    return partner_success(data)


@router.post('/saveOrUpdate', description="更新保存项目", dependencies=[Depends(user_auth_verify)])
# @permission_required(g.token)
async def save_or_update(params: LeakfixIn):
    logger.debug("服务器更新...")
    data = await LeakfixService.save_or_update(params)
    return partner_success(data)


@router.post('/deleted', description="删除")
@permission_required(g.token)
async def deleted(params: LeakfixId):
    """ 删除，逻辑删除，文件没有删除 """
    data = await LeakfixService.deleted(params)
    return partner_success(data)


@router.get('/download/{file_id}', description="文件下载")
async def download(file_id: str):
    data = await LeakfixService.download(file_id)
    return data


