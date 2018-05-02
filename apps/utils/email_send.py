from users.models import EmailVerifyRecord
from django.core.mail import send_mail
import random
import string
from mxonline.settings import EMAIL_FROM


def random_str(random_length=8):
    sample_chars = string.ascii_letters + string.digits
    random_chars = ''.join(random.sample(sample_chars, random_length))
    return random_chars


def send_register_email(email, send_type='register'):
    """
    发送邮箱的方法
    """
    # 实例化一个邮箱发送记录
    email_record = EmailVerifyRecord()

    # send_type生成不同位数的随机字符串
    if send_type == 'update':
        code = random_str(4)
    else:
        code = random_str(16)

    # 保存发送记录
    # 可以直接用
    # email_record = EmailVerifyRecord(code=code, email=email, send_type=send_type )
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = ''
    email_body = ''

    # 根据不同的send_type编写不通的邮件内容
    if send_type == 'register':
        email_title = '慕学在线网激活连接'
        email_body = '请点击一下连接完成注册：http://localhost:8000/active/%s' % code

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = '慕学在线网注册密码重置链接'
        email_body = '请点击下面的链接重置你的密码：http://localhost:8000/reset/%s' % code

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass

    elif send_type == 'update':
        email_title = '慕学在线网邮箱修改链接'
        email_body = '邮箱验证码为：'+code

        # 通过django自带的邮件发送方法发送邮件
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
