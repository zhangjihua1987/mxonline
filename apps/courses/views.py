from django.shortcuts import render
from django.views.generic import View
from .models import Course
from operation.models import UserFavorite, UserCourse, CourseComments
from courses.models import Video
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from apps.utils.mixin_utils import LoginRequiredMixin
from django.db.models import Q
# Create your views here.


class CourseListView(View):
    def get(self, request):

        current_nav = 'courses_list'

        # 取出所有课程
        all_courses = Course.objects.all()

        # 取出前端传回的sort值
        sort = request.GET.get('sort', '')

        # 根据传回的sort值排序
        if sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')
        elif sort == 'students':
            all_courses = all_courses.order_by('-students_nums')
        else:
            all_courses = all_courses.order_by('-add_time')

        # 取出3个热门课程
        hot_courses = all_courses.order_by('-click_nums')[:3]

        key_words = request.GET.get('keywords', '')
        if key_words:
            all_courses = all_courses.filter(Q(name__icontains=key_words) |
                                             Q(detail__icontains=key_words) |
                                             Q(desc__icontains=key_words))


        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 6, request=request)

        courses = p.page(page)
        return render(request, 'course-list.html', {
            'all_courses': all_courses,
            'courses': courses,
            'sort': sort,
            'hot_courses': hot_courses,
            'current_nav': current_nav
        })


class CourseDetailView(View):
    def get(self, request, course_id):

        # 利用前端传入的course_id查找对应课程
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        # 取出课程类别，在数据库中查询相同类别的2个课程作为推荐课程
        category = course.category
        if category:
            relate_courses = Course.objects.filter(category=category)[:2]

        # 弱为查询到相关课程，则返回空列表，否则在前端作for循环会报错
        else:
            relate_courses = []

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 判断登录用户是否收藏课程或机构
        has_fav_course = False
        has_fav_course_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_course_org = True

        # 将数据传递回前端
        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_course_org': has_fav_course_org
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    需要用户登录，首先继承LoginRequiredMixin类， 再继承View
    """
    def get(self, request, course_id):

        # 根据前端传入的course_id取出相应的课程
        course = Course.objects.get(id=course_id)

        # 点击我要学习后，首先判断该用户是否已与该课程关联
        user_course = UserCourse.objects.filter(user=request.user, course_id=course_id)
        if not user_course:

            # 若课程与用户未关联就建立关联
            user_course = UserCourse(user=request.user, course_id=course_id)
            user_course.save()
            course.students_nums += 1
            course.save()
        # 根据课程的id取到对应user_courses
        user_courses = UserCourse.objects.filter(course_id=course.id)

        # 根据user_courses取到学习到该课程的user_id
        users_id = [user_course.user_id for user_course in user_courses]

        # 根据学习到过该课程的user_id取到所有的相关relate_user_courses
        relate_user_courses = UserCourse.objects.filter(user_id__in=users_id)

        # 根据relate_user_courses取到相关课程的id
        relate_courses_id = [relate_user_course.course_id for relate_user_course in relate_user_courses]

        # 根据relate_courses_id取到相关课程
        relate_courses = Course.objects.filter(id__in=relate_courses_id)

        # 将数据传到前端
        return render(request, 'course-video.html', {
            'course': course,
            'relate_courses': relate_courses
        })


class CourseCommentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        all_comments = course.coursecomments_set.all().order_by('-add_time')

        # 根据课程的id取到对应user_courses
        user_courses = UserCourse.objects.filter(course_id=course.id)

        # 根据user_courses取到学习到该课程的user_id
        users_id = [user_course.user_id for user_course in user_courses]

        # 根据学习到过该课程的user_id取到所有的相关relate_user_courses
        relate_user_courses = UserCourse.objects.filter(user_id__in=users_id)

        # 根据relate_user_courses取到相关课程的id
        relate_courses_id = [relate_user_course.course_id for relate_user_course in relate_user_courses]

        # 根据relate_courses_id取到相关课程
        relate_courses = Course.objects.filter(id__in=relate_courses_id)[:5]

        # 将数据传到前端
        return render(request, 'course-comment.html', {
            'course': course,
            'all_comments': all_comments,
            'relate_courses': relate_courses
        })


class AddCommentView(View):
    def post(self, request, course_id):

        # 这里由于前端做了未登录页面跳转的逻辑，所以这里要判断用户是否登录
        if not request.user.is_authenticated:

            # 判断未登录 根据前端定义的名称，返回json代码
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')
        else:

            # 判断登录后，根据前端定义的名称，获取评论信息
            comments = request.POST.get('comments', '')

            # 判断如果评论不为空，并且传递的course_id大于0
            if comments and int(course_id) > 0:

                # 根据course_id, comments, user信息实例化CourseComments
                course_comments = CourseComments(course_id=course_id, comments=comments, user=request.user)

                # 保存该信息
                course_comments.save()

                # 根据前端定义的名称，返回json代码
            return HttpResponse('{"status": "success"}', content_type='application/json')


class VideoView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        course = video.lesson.course
        course_id = course.id

        # 点击我要学习后，首先判断该用户是否已与该课程关联
        user_course = UserCourse.objects.filter(user=request.user, course_id=course_id)
        if not user_course:
            # 若课程与用户未关联就建立关联
            user_course = UserCourse(user=request.user, course_id=course_id)
            user_course.save()
        # 根据课程的id取到对应user_courses
        user_courses = UserCourse.objects.filter(course_id=course.id)

        # 根据user_courses取到学习到该课程的user_id
        users_id = [user_course.user_id for user_course in user_courses]

        # 根据学习到过该课程的user_id取到所有的相关relate_user_courses
        relate_user_courses = UserCourse.objects.filter(user_id__in=users_id)

        # 根据relate_user_courses取到相关课程的id
        relate_courses_id = [relate_user_course.course_id for relate_user_course in relate_user_courses]

        # 根据relate_courses_id取到相关课程
        relate_courses = Course.objects.filter(id__in=relate_courses_id)

        # 将数据传到前端
        return render(request, 'course-play.html', {
            'course': course,
            'relate_courses': relate_courses,
            'video': video
        })


