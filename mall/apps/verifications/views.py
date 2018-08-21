from random import randint

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView

from libs.yuntongxun.sms import CCP
from .serializers import RegisterSMSCodeSerializer
from rest_framework.response import Response


class RegisterImageCodeView(APIView):
    """
    生成验证码
    GET verifications/imagecodes/(?P<image_code_id>.+)/
    需要通过JS生成一个唯一码,以确保后台对图片进行校验
    """

    def get(self, request, image_code_id):
        """

        通过第三方库,生成图片和验证码,我们需要对验证码进行redis保存
        1创建图片和验证码
        2通过redis进行保存验证码,需要在设置中添加 验证码数据库选项
        3将图片返回
        """
        # 1创建图片和验证码
        text, image = captcha.generate_captcha()
        # 2通过redis进行保存验证码,需要在设置中添加 验证码数据库选项
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s' % image_code_id, 60, text)
        # 3将图片返回
        return HttpResponse(image, content_type='image/jpeg')


class RegisterSMSCodeView(GenericAPIView):
    """
    获取短信验证码
     GET /verifications/smscodes/(?P<mobile>1[345789]\d{9})/?text=xxxx & image_code_id=xxxx
     获取短信验证码,首先需要校验,验证码

    # 1创建序列化器,定义text 和 image_code_id
    # 2redis 判断该用户是否频繁获取
    # 3生成短信验证码
    # 4redis增加记录
    # 5发送短信
    # 6返回响应
    """
    serializer_class = RegisterSMSCodeSerializer

    def get(self, request, mobile):
        """
        # 1创建序列化器,定义text 和 image_code_id
        # 2redis 判断该用户是否频繁获取
        # 3生成短信验证码
        # 4redis增加记录
        # 5发送短信
        # 6返回响应

        """
        # 1创建序列化器,定义text 和 image_code_id
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 2redis 判断该用户是否频繁获取
        redis_conn = get_redis_connection('code')

        if redis_conn.get('sms_flag_%s' % mobile):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 3生成短信验证码
        sms_code = '%06d' % randint(0, 999999)

        # 4redis增加记录
        redis_conn.setex('sms_%s' % mobile, 5 * 60, sms_code)
        redis_conn.setex('sms_flag_%s' % mobile, 60, 1)

        # 5发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, 5], 1)

        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)

        # 6返回响应
        return Response({'message': 'ok'})
