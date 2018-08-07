# coding:utf8

from celery import Celery

# 进行Celery允许配置
# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

# 创建一个 celery对象
# celery 的第一个参数 main 习惯上给它设置 脚本路径就可以, 脚本路径是唯一的
app = Celery('celery_tasks')

# 我们需要在这里 设置broker
# 我们是通过加载 config的配置文件来设置 broker
# config_from_object 填写的 broker的文件路径
app.config_from_object('celery_tasks.config')

# 我们需要celey自动检测该任务
# 里边的任务是 通过 脚本路径来实现的
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])




# worker 的执行是通过指令来实现分配的
# celery -A celery实例对象的脚本路径  worker -l info

# celery -A celery_tasks.main   worker -l info
