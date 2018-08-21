from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from .serializers import RegisterCreateSerializer, UserDetailSerializer, EmailSerializer, AddressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class RegisterUsernameCountAPIView(APIView):
    """
    获取用户名的个数
     GET /users/usernames/(?P<username>\w{5,20})/count/
    """

    def get(self, request, username):
        # 通过模型查询,获取用户名个数
        count = User.objects.filter(username=username).count()
        # 组织数据
        context = {
            'count': count,
            'username': username
        }

        # 返回响应
        return Response(context)


class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET: /users/phones/(?P<mobile>1[345789]\d{9})/count/
    """

    def get(self, request, mobile):
        # 通过模型查询获取手机号码个数
        count = User.objects.filter(mobile=mobile).count()
        # 组织数据
        context = {
            'count': count,
            'mobile': mobile
        }

        # 返回响应
        return Response(context)


class RegisterCreateView(CreateAPIView):
    """
    用户注册
     POST /users/
     用户注册我们需要对数据进行校验,同时需要数据入库
    """
    serializer_class = RegisterCreateSerializer


class UserDetailView(RetrieveAPIView):
    """
    获取登录用户信息
     GET/users/infos/
      既然是登录用户,我们就要用到权限管理
    在类视图对象中也保存了请求对象request
    request对象的user属性是通过认证检验之后的请求用户对象
    """
    permission_classes = [IsAuthenticated]

    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """
    保存邮箱
    PUT/users/emails/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class VerifivationEmailView(APIView):
    """
    验证激活邮箱
    GET /users/emails/verification/?token=xxxx
    """

    def get(self, request):
        """
        # 1获取token,并判断
        # 2获取token中的Id
        # 3查询用户,并判断是否存在
        # 4修改状态
        # 5返回响应
        """
        # 1获取token,并判断
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 2获取token中的Id
        # 3查询用户,并判断是否存在
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接无效'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            # 4修改状态
            user.email_active = True
            user.save()
            # 5返回响应
            return Response({'message': 'ok'})


class AddressViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    list GET: /users/addresses/
    create POST: /users/addresses/
    destroy DELETE: /users/addresses/
    action PUT: /users/addresses/pk/status/
    action PUT: /users/addresses/pk/title/
    """
    # 制定序列化器
    serializer_class = AddressSerializer
    # 添加用户权限
    permission_classes = [IsAuthenticated]

    # 由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据

        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message': '保存地址数量已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 返回响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })
