# -*- coding: utf-8 -*-
# @author: xiaobai

from autotest.db.session import async_engine
from autotest.models.base import Base
from autotest.models import ui_models
from autotest.models import api_models
from autotest.models import celery_beat_models
from autotest.models import coverage_models
from autotest.models import system_models
from autotest.models import tools_models


async def init_db():
    """
    初始化数据库
    :return:
    """
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
