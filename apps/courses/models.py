from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher
from DjangoUeditor.models import UEditorField

# Create your models here.


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name='课程机构', null=True, blank=True, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, verbose_name='讲师', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='课程名称')
    desc = models.CharField(max_length=100, verbose_name='课程描述')
    detail = models.TextField(verbose_name='课程详情')
    degree = models.CharField(choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), max_length=2, verbose_name='难度')
    learn_time = models.IntegerField(default=0, verbose_name='学习时长（分钟）')
    students_nums = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    image = models.ImageField(upload_to='course/%Y/%m', verbose_name='封面')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    category = models.CharField(default='后端开发', max_length=20, verbose_name='课程类别')
    course_requirements = models.CharField(default='', max_length=300, verbose_name='课程须知')
    teacher_told = models.CharField(default='', max_length=300, verbose_name='讲师告知')
    is_banner = models.BooleanField(default=False, verbose_name='是否轮播')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    # 获取章节数
    def get_lessons_num(self):
        return self.lesson_set.all().count()
    get_lessons_num.short_description = '章节数'

    # 获取5个学习用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    # 获取课程所有章节
    def get_lessons(self):
        return self.lesson_set.all()

    # 获取所有资源
    def get_recources(self):
        return self.courseresource_set.all()

    def __str__(self):
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        proxy = True


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    #获取章节视频
    def get_videos(self):
        return self.video_set.all()

    def __str__(self):
        return '%s %s' % (self.course, self.name)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='章节')
    name = models.CharField(max_length=100, verbose_name='视频名')
    url = models.CharField(max_length=200, default='', verbose_name='视频地址')
    learn_time = models.IntegerField(default=0, verbose_name='学习时长（分钟）')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.lesson, self.name)


class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='资源名称')
    download = models.FileField(upload_to='course/resource/%Y/%m', verbose_name='资源文件', max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.course, self.name)
