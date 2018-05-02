from django.urls import path, include,re_path
from .views import CourseListView, CourseDetailView, CourseInfoView, CourseCommentView, AddCommentView, VideoView

app_name = 'courses'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
    re_path(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    re_path(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),
    re_path(r'^comment/(?P<course_id>\d+)/$', CourseCommentView.as_view(), name='course_comment'),
    re_path(r'^comment/add_comment/(?P<course_id>\d+)/$', AddCommentView.as_view(), name='add_comment'),
    re_path(r'^video/(?P<video_id>\d+)/$', VideoView.as_view(), name='video_play')
]
