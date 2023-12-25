from django.urls import path
from ..views import animals_views as views

urlpatterns = [
    path('species', views.SpeciesAPIView.as_view(), name='SpeciesAPIView'),
    path('species/search', views.SpeciesSearchAPIView.as_view()),
    path('species/short', views.SpeciesShortDetailsApiView.as_view()),
    path('animal', views.AnimalApiView.as_view(), name='AnimalAPIView'),
    path('costscategory', views.CostCategoryAPIView.as_view()),
    path('singlecostscategory', views.SingleCostCategoryAPIView.as_view()),
    path('vaccination', views.VaccinationAPIView.as_view()),
    path('health', views.HelathAPIView.as_view()),
    path('costs', views.CostsAPIView.as_view()),
    path('latestcosts', views.LatestCostsAPIView.as_view()),
    path('animalSpecies', views.FarmerAnimalSpeciesFilterAPIView.as_view()),
    path('animalSpeciesResult', views.FarmerAnimalSpeciesResultAPIView.as_view())
]