import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse
from organization.models import CourseOrg


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree',
                    'learn_time', 'students_nums', 'fav_nums',
                    'image', 'click_nums', 'add_time', 'course_org',
                    'get_lessons_num']

    search_fields = ['name', 'desc', 'detail', 'degree',
                     'students_nums', 'fav_nums',
                     'image', 'click_nums', 'course_org']

    list_filter = ['name', 'desc', 'detail', 'degree',
                   'learn_time', 'students_nums', 'fav_nums',
                   'image', 'click_nums', 'add_time', 'course_org__name']

    # 根据点击数倒序排列
    ordering = ['-click_nums']

    # 只读字段的设置
    readonly_fields = ['click_nums', 'fav_nums', 'students_nums', 'add_time']

    inlines = [LessonInline]

    list_editable = ['degree']

    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        """
        在保存课程的时候统计课程机构的数量
        """
        # 取当前的实例
        obj = self.new_obj
        obj.save()
        course_org = obj.course_org
        if course_org is not None:
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    # style_fields = {'detail': 'ueditor'}


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree',
                    'learn_time', 'students_nums', 'fav_nums',
                    'image', 'click_nums', 'add_time', 'course_org']

    search_fields = ['name', 'desc', 'detail', 'degree',
                     'students_nums', 'fav_nums',
                     'image', 'click_nums', 'course_org']

    list_filter = ['name', 'desc', 'detail', 'degree',
                   'learn_time', 'students_nums', 'fav_nums',
                   'image', 'click_nums', 'add_time', 'course_org__name']

    # 根据点击数倒序排列
    ordering = ['-click_nums']

    # 只读字段的设置
    readonly_fields = ['click_nums', 'fav_nums', 'students_nums', 'add_time']

    inlines = [LessonInline]

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs

    def save_models(self):
        """
        在保存课程的时候统计课程机构的数量
        """
        # 取当前的实例
        obj = self.new_obj
        obj.save()
        course_org = obj.course_org
        if course_org is not None:
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    # style_fields = {'detail': 'ueditor'}


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson__name', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
