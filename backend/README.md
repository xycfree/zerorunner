
#### 🌈 介绍

基于 python + fastApi + celery + sqlalchemy + redis

- 使用软件版本
- python version 3.9.6
- mysql version 8.0.23
- redis version 6.0.9
- node version 18.15.0

#### 💒 平台地址地址
- github 
https://github.com/baizunxian/zerorunner
- gitee

#### ⛱️ 线上预览

- ZERORUNNER 自动化测试平台在线预览 <a href="https://waltercodes.com:8888" target="_blank">https://waltercodes.com:8888</a>


#### 🚧 项目启动初始化

```bash
# 克隆项目
git clone https://github.com/baizunxian/zerorunner.git

# 数据库脚本 将内容复制数据库执行 需要新建数据库 zerorunner
db_script/db_init.sql
# 初始化数据脚本 将内容复制数据库执行 
db_script/init.sql  

# 修改对应的数据库地址，redis 地址
autotest/config.py

# 安装依赖
pip install -r  requirements

# 运行项目 zerorunner/backend 目录下执行
python main.py

# 异步任务依赖 job 启动命令

#  windows 启动，只能单线程 zerorunner/backend 目录下执行
celery -A celery_worker.worker.job worker --pool=solo -l INFO 

celery -A celery_worker.worker  worker --pool=solo -l INFO 



# linux 启动
celery -A celery_worker.worker.job worker --loglevel=INFO -c 10 -P solo -n zerorunner-job-worker

# 定时任务启动
celery -A celery_worker.worker.job beat -S celery_worker.scheduler.schedulers:DatabaseScheduler -l INFO

# 定时任务心跳启动
celery -A celery_worker.worker.job beat  -l INFO 
celery -A celery_worker.worker beat  -l INFO 



# alembic迁移命令
https://thedmitry.pw/blog/2023/08/fastapi-async-sqlalchemy-pytest-and-alembic/
# 新增表需要在autotest/models/__init__.py文件中导入表文件

# alembic async 配置参考
# https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/blob/main/backend/app/alembic/env.py

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"当前路径:{BASE_DIR}")
sys.path.insert(0, BASE_DIR)
# SQLALCHEMY 模式需要导入 Base
from autotest.models.base import Base
target_metadata = Base.metadata  # SQLALCHEMY 模式同步
# target_metadata = SQLModel.metadata  # sqlmodel 模式同步

alembic init alembic  # 初始化
alembic init -t async alembic  # 异步初始化

alembic revision --autogenerate -m "init"  # 提交修改
alembic upgrade head  # 更新
alembic downgrade head  # 降级

# merge主分支
1.查看远程仓库: git remote -v 
2.添加远项目地址: git remote add xyc git@github.com:baizunxian/zerorunner.git
3.检出远程分支更新: git fetch xyc  
4.merge远程分支到本地: git merge xyc/master
undefined.文件推送: git  push

```
#### 💌 支持作者

如果觉得框架不错，或者已经在使用了，希望你可以去 <a target="_blank" href="https://github.com/baizunxian/zerorunner">Github</a> 帮我点个 ⭐ Star，这将是对我极大的鼓励与支持, 平台会持续迭代更新。
