from django.urls import path, include
from .views import WorkerCountAPIView, TaskRatioAPIView, AnimalCostSumAPIView, AnimalCostByCategoryAPIView, HealthRatioAPIView, CategoryCostAPIView, CostFromLastSixMonthsAPIView, PdfReportAPIView

urlpatterns = [
   path('countedworkers', WorkerCountAPIView.as_view()),
   path('taskratio', TaskRatioAPIView.as_view()),
   path('healthratio', HealthRatioAPIView.as_view()),
   path('animalcostsum', AnimalCostSumAPIView.as_view()),
   path('animalcostbycategory', AnimalCostByCategoryAPIView.as_view()),
   path('categoryCosts', CategoryCostAPIView.as_view()),
   path('costssixmonths', CostFromLastSixMonthsAPIView.as_view()),
   path('pdf', PdfReportAPIView.as_view()),
]