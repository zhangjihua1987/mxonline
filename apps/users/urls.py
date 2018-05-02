from django.urls import path, include, re_path
from .views import UserInfoView, UploadImageView, UpdatePWD, SendUpdateEmailView, UpdateEmailView, MyCourseView
from .views import MyFavOrgView, MyFavCourseView, MyFavTeacherView, MyMessageView

app_name = 'users'

urlpatterns = [
    # 个人主页url
    path('info/', UserInfoView.as_view(), name='user_info'),

    # 修改头像url
    path('upload_image/', UploadImageView.as_view(), name='upload_image'),

    # 修改密码url
    path('update/pwd/', UpdatePWD.as_view(), name='update_pwd'),

    # 发送修改邮箱验证码
    path('sendemail_code/', SendUpdateEmailView.as_view(), name='sendemail_code'),

    # 修改邮箱url
    path('update_email/', UpdateEmailView.as_view(), name='update_email'),

    # 我的课程url
    path('my_course/', MyCourseView.as_view(), name='my_course'),

    # 我的机构收藏
    path('my_fav/org', MyFavOrgView.as_view(), name='my_fav_org'),

    # 我的收藏课程
    path('my_fav/course', MyFavCourseView.as_view(), name='my_fav_course'),

    # 我的讲师收藏
    path('my_fav/teacher', MyFavTeacherView.as_view(), name='my_fav_teacher'),

    # 个人消息
    path('my_message/', MyMessageView.as_view(), name='my_message')
]
