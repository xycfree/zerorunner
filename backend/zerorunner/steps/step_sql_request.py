# -*- coding: utf-8 -*-
# @author: xiaobai
import time
import typing

from loguru import logger

from zerorunner.database.engine import DBEngine
from zerorunner.model.result_model import SqlSessionData
from zerorunner.model.step_model import TStep, TSqlRequest
from zerorunner.models import TStepLogType, StepResult, TStepResultStatusEnum
from zerorunner.runner import SessionRunner
from zerorunner.steps.base import IStep
from zerorunner.steps.step_result import TStepResult


def run_sql_request(runner: SessionRunner,
                    step: TStep,
                    step_tag: str = None,
                    parent_step_result: StepResult = None):
    step_result = TStepResult(step, step_tag=step_tag)
    step_result.start_log()
    start_time = time.time()
    try:
        step_variables = runner.get_merge_variable(step)
        request_dict = step.sql_request.dict()
        # 合并变量
        parsed_request_dict = runner.parser.parse_data(request_dict, step_variables)
        step.sql_request = TSqlRequest(**parsed_request_dict)
        step_result.result.sql_session_data = SqlSessionData(**step.sql_request.dict(exclude={'password'}))

        db_engine = DBEngine(
            f'mysql+pymysql://{step.sql_request.user}:'
            f'{step.sql_request.password}@{step.sql_request.host}:'
            f'{step.sql_request.port}/{step.sql_request.database}'
            f"?charset=utf8mb4"
        )

        data = db_engine.fetchall(step.sql_request.sql)
        variables = {step.sql_request.variable_name: data}
        runner.with_variables(variables)
        step_result.result.export_vars.update(variables)
        logger.info(f"SQL查询---> {step.sql_request.sql}")
        step_result.start_log(f"SQL查询-> 设置变量:{step.sql_request.variable_name}, 设置变量值：{data}")
        runner.with_session_variables(variables)
        step_result.result.sql_session_data.execution_result = data
        step_result.result.sql_session_data.success = True
        step_result.set_step_result_status(TStepResultStatusEnum.success)

    except Exception as err:
        step_result.set_step_result_status(TStepResultStatusEnum.err)
        step_result.result.sql_session_data.success = False
        raise
    finally:
        step_result.end_log()
        step_result = step_result.get_step_result()
        step_result.duration = time.time() - start_time
        runner.append_step_result(step_result=step_result,
                                  step_tag=step_tag,
                                  parent_step_result=parent_step_result)


class RequestWithOptionalArgs(IStep):
    def __init__(self, step: TStep):
        self.__step = step

    def with_host(self, host: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.host = host
        return self

    def with_port(self, port: typing.Union[int, str]) -> "RequestWithOptionalArgs":
        self.__step.sql_request.port = port
        return self

    def with_user(self, user: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.user = user
        return self

    def with_password(self, password: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.password = password
        return self

    def with_sql(self, sql: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.sql = sql
        return self

    def with_timeout(self, timeout: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.timeout = timeout
        return self

    def with_variable_name(self, variable_name: str) -> "RequestWithOptionalArgs":
        self.__step.sql_request.variable_name = variable_name
        return self

    def teardown_hook(
            self, hook: str,
            assign_var_name: str = None
    ) -> "RequestWithOptionalArgs":
        if assign_var_name:
            self.__step.teardown_hooks.append({assign_var_name: hook})
        else:
            self.__step.teardown_hooks.append(hook)

        return self

    def struct(self) -> TStep:
        return self.__step

    def name(self) -> str:
        return self.__step.name

    def type(self) -> str:
        return f"request-{self.__step.request.method}"

    def run(self, runner: SessionRunner, **kwargs):
        return run_sql_request(runner, self.__step)


class RunSqlRequest(object):
    def __init__(self, name: str):
        self.__step = TStep(name=name)

    def with_step(self, step: TStep):
        self.__step = step
        return self

    def with_variables(self, **variables) -> "RunSqlRequest":
        self.__step.variables.update(variables)
        return self

    def with_retry(self, retry_times, retry_interval) -> "RunSqlRequest":
        self.__step.retry_times = retry_times
        self.__step.retry_interval = retry_interval
        return self

    def setup_hook(self, hook: str, assign_var_name: str = None) -> "RunSqlRequest":
        if assign_var_name:
            self.__step.setup_hooks.append({assign_var_name: hook})
        else:
            self.__step.setup_hooks.append(hook)

        return self


class RunSqlStep(IStep):
    def __init__(self, step: TStep):
        self.__step = step

    def name(self) -> str:
        return self.__step.name

    def type(self) -> str:
        return self.__step.step_type

    def struct(self) -> TStep:
        return self.__step

    def run(self, runner: SessionRunner, **kwargs):
        return run_sql_request(runner, self.__step, **kwargs)
