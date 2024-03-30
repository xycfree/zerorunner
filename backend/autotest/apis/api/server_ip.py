import requests
from fastapi import APIRouter, Depends

from autotest.utils.local import g
from autotest.utils.response.http_response import partner_success
from autotest.schemas.api.serverip_query import ServerIpQuery, ServerIpIn, ServerIpId
from autotest.services.api.server_ip import ServerIPService
from autotest.services.system.user import UserService, permission_required, user_auth_verify
from loguru import logger

router = APIRouter()


@router.post('/list', description="服务器列表")
async def server_list(params: ServerIpQuery):
    logger.debug(f"project list params: {params}, request data: {await g.request.json()}")
    data = await ServerIPService.list(params)
    return partner_success(data)


@router.post('/getAllServerip', description="获取所有服务器信息")
async def get_all_serverip():
    data = await ServerIPService.get_all()
    return partner_success(data)


@router.post('/saveOrUpdate', description="更新保存项目", dependencies=[Depends(user_auth_verify)])
# @permission_required(g.token)
async def save_or_update(params: ServerIpIn):
    logger.debug("服务器更新...")
    data = await ServerIPService.save_or_update(params)
    return partner_success(data)


@router.post('/deleted', description="删除", dependencies=[Depends(user_auth_verify)])
# @permission_required(g.token)
async def deleted(params: ServerIpId):
    data = await ServerIPService.deleted(params)
    return partner_success(data)



