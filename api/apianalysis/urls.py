from django.urls import path, include
from .views import WorkerCountAPIView, TaskRatioAPIView, AnimalCostSumAPIView, AnimalCostByCategoryAPIView, HealthRatioAPIView, CategoryCostAPIView, CostFromLastSixMonthsAPIView, PdfFullReportAPIView, PdfFullCostsReportAPIView, PdfFullHealthReportAPIView, PdfMonthlyReportAPIView, PdfMonthlyCostsReportAPIView, PdfMonthlyHealthReportAPIView

urlpatterns = [
   path('countedworkers', WorkerCountAPIView.as_view()),
   path('taskratio', TaskRatioAPIView.as_view()),
   path('healthratio', HealthRatioAPIView.as_view()),
   path('animalcostsum', AnimalCostSumAPIView.as_view()),
   path('animalcostbycategory', AnimalCostByCategoryAPIView.as_view()),
   path('categoryCosts', CategoryCostAPIView.as_view()),
   path('costssixmonths', CostFromLastSixMonthsAPIView.as_view()),
   path('pdf', PdfFullReportAPIView.as_view()),
   path('pdfFullCosts', PdfFullCostsReportAPIView.as_view()),
   path('pdfFullHealth', PdfFullHealthReportAPIView.as_view()),
   path('pdfMonthly', PdfMonthlyReportAPIView.as_view()),
   path('pdfMonthlyCosts', PdfMonthlyCostsReportAPIView.as_view()),
   path('pdfMonthlyHealth', PdfMonthlyHealthReportAPIView.as_view()),
]