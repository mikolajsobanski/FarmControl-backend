from django.urls import path, include
from .views import WorkerCountAPIView, TaskRatioAPIView, AnimalCostSumAPIView, AnimalCostByCategoryAPIView

urlpatterns = [
   path('countedworkers', WorkerCountAPIView.as_view()),
   path('taskratio', TaskRatioAPIView.as_view()),
   path('animalcostsum', AnimalCostSumAPIView.as_view()),
   path('animalcostbycategory', AnimalCostByCategoryAPIView.as_view()),
]