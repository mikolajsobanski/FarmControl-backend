from django.urls import path
from ..views import utils_views as views
urlpatterns = [
    path('note', views.NoteAPIView.as_view()),
    path('task', views.TaskAPIView.as_view()),
    path('taskInprogress', views.GetInProgressTaskAPIView.as_view()),
    path('taskComplete', views.GetCompleteTaskAPIView.as_view()),
    path('makeComplete', views.MakeCompleteTaskAPIView.as_view()),
    path('makeInprogress', views.MakeInProgressTaskAPIView.as_view()),
    path('taskComment', views.TaskCommentsAPIView.as_view()),
]
