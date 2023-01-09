from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save/', views.save, name='save'),
    path('delete/', views.delete, name='delete'),
    path('results.json', views.results, name='results'),
    path('show/', views.show, name='show'),
]
