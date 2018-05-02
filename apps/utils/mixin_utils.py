from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    """
    登录需求的类，用于需要验证用户是否登录时被继承
    """
    # 配置login_url，未登录时跳转到登录页面
    @method_decorator(login_required(login_url='/login/'))
    # 传入参数以及返回值的编写方式
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

