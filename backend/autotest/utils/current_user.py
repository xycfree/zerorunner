# -*- coding: utf-8 -*-
# @author: walter
import typing

from autotest.db.my_redis import redis_pool
from autotest.exceptions.exceptions import AccessTokenFail
from autotest.utils.consts import TEST_USER_INFO
from autotest.utils.local import g


async def current_user(token: str = None) -> typing.Union[typing.Dict[typing.Text, typing.Any], None]:
    # 为了解决alembic更新导致的互相导入冲突的问题 most likely due to a circular import
    from autotest.exceptions.exceptions import AccessTokenFail

    """根据token获取用户信息"""

    user_info = await redis_pool.redis.get(TEST_USER_INFO.format(g.token if not token else token))
    if not user_info:
        raise AccessTokenFail()
    return user_info
