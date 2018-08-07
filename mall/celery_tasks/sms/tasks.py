# coding:utf8
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app


# 任务
# 我们的任务需要用 celery实例对象的 task 装饰器 装饰

# task 中的name 参数 是表示 任务的名字 name='aaaaa'

@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, 5], 1)
