import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import UserProfile, EmailVerifyRecord, Banner
from courses.models import Course, Teacher
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg
from django.views.generic.base import View
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UpdateEmailForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

# 导入reverse方法
from django.urls import reverse


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None
# Create your views here.


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
            return render(request, 'login.html', {})
        else:
            return render(request, 'active_fail.html', {})


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已经存在'})
            pass_word = request.POST.get('password', '')
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 发送欢迎注册消息
            user_message = UserMessage(user=user_profile.id)
            user_message.message = '欢迎注册'
            user_message.save()

            send_register_email(user_name, send_type='register')
            return render(request, 'login.html', {})
        else:
            return render(request, 'register.html', {'register_form': register_form})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    # 通过HttpResponseRedirect重定向到首页
                    # 首页地址可以用url名通过reverse方法反解为绝对路径
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class LogOutView(View):
    """
    登出功能
    """
    def get(self, request):
        logout(request)

        # 通过HttpResponseRedirect重定向到首页
        # 首页地址可以用url名通过reverse方法反解为绝对路径
        return HttpResponseRedirect(reverse('index'))


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, send_type='forget')
            return render(request, 'send_success.html', {})
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    def get(self, request, reset_code):
        all_records = EmailVerifyRecord.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_fail.html', {})


class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致'})
            else:
                user = UserProfile.objects.get(email=email)
                user.password = make_password(pwd1)
                user.save()
                return render(request, 'login.html', {})
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, 'usercenter-info.html', {
            'user': user
        })


class UploadImageView(LoginRequiredMixin, View):
    """
    处理用户上传图片的view
    """
    def post(self, request):

        # 实例化一个UploadImageForm
        # 文件格式的数据是保存在request.FILES里的，需要单独传递
        # 可以用instance=request.user将Model也实例
        upload_image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)

        # 判断form是否合法
        if upload_image_form.is_valid():

            # 可以直接用form将数据保存到数据库
            upload_image_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail"}', content_type='application/json')


class UpdatePWD(LoginRequiredMixin, View):
    """
    用户在个人中心修改密码
    """
    def post(self, request):

        # 修改密码的form可以用之前重置密码的form
        update_pwd_form = ModifyPwdForm(request.POST)

        # 以下逻辑与重置密码逻辑几乎一样，这里需要返回json格式的信息
        if update_pwd_form.is_valid():

            # 这里获取password的时候要确保与前端的名字是一致的才能获取到
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            user = request.user
            if pwd1 == pwd2:
                user.password = make_password(pwd1)
                user.save()
                return HttpResponse('{"status": "success"}', content_type='application/json')
            else:
                return HttpResponse('{"status": "fail", "msg": "两次密码不一致"}', content_type='application/json')
        else:
            # import json后可以直接用json.dumps将python dict转换给json格式
            return HttpResponse(json.dumps(update_pwd_form.errors), content_type='application/json')


class SendUpdateEmailView(LoginRequiredMixin, View):
    """
    向修改邮箱发送验证码
    """
    def get(self, request):

        # 用form验证输入的邮箱是否合法
        update_email_form = UpdateEmailForm(request.GET)
        if update_email_form.is_valid():
            email = request.GET.get('email', '')

            # 查找邮箱是否已存在
            if UserProfile.objects.filter(email=email):
                return HttpResponse('{"email": "邮箱已存在"}', content_type='application/json')
            else:

                # 调用之前的发送邮箱方法，在调用之前修改send_type字段，增加一个选项为修改邮箱
                send_register_email(email, send_type='update')
                return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(update_email_form.errors), content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """
    验证并修改邮箱
    """
    def post(self, request):

        # 获取前端传来的邮箱及验证码
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        # 查询发送记录是否存在
        if EmailVerifyRecord.objects.filter(code=code, email=email, send_type='update'):

            # 修改用户的email并保存
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"email": "验证码错误"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """
    def get(self, request):
        user = request.user
        all_user_courses = UserCourse.objects.filter(user=user)
        all_mycourse_id = [user_course.course_id for user_course in all_user_courses]
        all_mycourses = Course.objects.filter(id__in=all_mycourse_id)

        return render(request, 'usercenter-mycourse.html', {
            'all_mycourses': all_mycourses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我的收藏机构
    """
    def get(self, request):
        user = request.user

        # 通过user查询出收藏记录
        user_fav_orgs = UserFavorite.objects.filter(user=user, fav_type=2)

        # 获取user所有收藏机构的id
        user_fav_org_id = [user_fav_org.fav_id for user_fav_org in user_fav_orgs]

        # 通过将所有收藏机构的id通过__in方法将查询出来
        all_user_fav_orgs = CourseOrg.objects.filter(id__in=user_fav_org_id)

        # 传递到前端
        return render(request, 'usercenter-fav-org.html', {
            'all_user_fav_orgs': all_user_fav_orgs
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我的收藏课程
    """
    def get(self, request):
        user = request.user
        user_fav_courses = UserFavorite.objects.filter(user=user, fav_type=1)
        user_fav_courses_id = [user_fav_course.fav_id for user_fav_course in user_fav_courses]
        all_user_fav_courses = Course.objects.filter(id__in=user_fav_courses_id)

        return render(request, 'usercenter-fav-course.html', {
            'all_user_fav_courses': all_user_fav_courses
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我的收藏讲师
    """
    def get(self, request):
        user = request.user
        user_fav_teachers = UserFavorite.objects.filter(user=user, fav_type=3)
        user_fav_teachers_id = [user_fav_teacher.fav_id for user_fav_teacher in user_fav_teachers]
        all_fav_teachers = Teacher.objects.filter(id__in=user_fav_teachers_id)

        return render(request, 'usercenter-fav-teacher.html', {
            'all_fav_teachers': all_fav_teachers
        })


class MyMessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    def get(self, request):
        user_id = request.user.id

        # 根据user.id查询出所有未读消息
        unread_messages = UserMessage.objects.filter(user=user_id, has_read=False)
        # 将未读消息标记为已读
        for unread_message in unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 根据user.id查询出所有消息
        all_my_messages = UserMessage.objects.filter(user=user_id)

        # 分页功能
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_my_messages, 5, request=request)
        my_messages = p.page(page)

        # 将数据传递到前端
        return render(request, 'usercenter-message.html', {
            'my_messages': my_messages
        })


class IndexView(View):
    """
    主页功能
    """
    def get(self, request):
        banners = Banner.objects.all().order_by('banner_index')[:5]
        banner_courses = Course.objects.filter(is_banner=True)[:4]
        courses = Course.objects.all()[:6]
        orgs = CourseOrg.objects.all()[:15]

        return render(request, 'index.html', {
            'banners': banners,
            'banner_courses': banner_courses,
            'courses': courses,
            'orgs': orgs
        })



