# coding:utf8
import re

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import User, Address
from django_redis import get_redis_connection


class RegisterCreateSerializer(serializers.ModelSerializer):
    """
    1用户再进行提交的时候有3个数据:passwords,sms_code,allow
    2进行校验:
        2.1单个字段的校验有 手机号码,是否同意协议
        2.2 多字段校验, 密码是否一致, 短信是否一致
    """
    # 1用户再进行提交的时候有3个数据:password2,sms_code,allow
    password2 = serializers.CharField(label='校验密码', allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6,
                                     allow_null=False, allow_blank=False, write_only=True)
    allow = serializers.CharField(label='是否同意协议', allow_null=False, allow_blank=False, write_only=True)

    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow',
                  'token')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 进行校验
    # 2.1单个字段的校验有 手机号码,是否同意协议
    def validate_mobile(self, value):

        if not re.match(r'1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号码格式不正确')
        return value

    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError('您未同意协议')
        return value

    # 2.2 多字段校验, 密码是否一致, 短信验证码是否一致
    def validate(self, attrs):

        # 两次密码比较
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 短信验证码是否一致
        # 获取用户提交的验证码
        code = attrs['sms_code']
        # 链接redis,获取redis中验证码
        redis_connn = get_redis_connection('code')
        # 获取手机号码
        mobile = attrs['mobile']
        redis_code = redis_connn.get('sms_%s' % mobile)
        # 判断验证码是否存在
        if redis_code is None:
            raise serializers.ValidationError('验证码已过期')
        # 判断短信验证码是否一致
        if redis_code.decode() != code:
            raise serializers.ValidationError('验证码不正确')

        return attrs

    def create(self, validated_data):

        # 删除多余字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)

        # 修改密码
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = validated_data['email']
        instance.save()

        # 发送激活邮件
        # 生成激活链接
        # verify_url = instance.generate_verify_email_url()
        # # 发送,调用delay方法
        # send_verify_mail.delay(email.verify_url)
        return instance


class AddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validated_data):
        # Address模型类中有user属性,将user对象添加到模型类的创建参数中
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)