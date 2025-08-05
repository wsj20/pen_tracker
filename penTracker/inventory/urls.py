from django.urls import path
from . import views

urlpatterns = [
    path('', views.pen_list, name='pen-list'),
    path('add/', views.add_pen, name='pen-add'),
    path('models/add', views.add_pen_model, name='pen-model-add'),
    path('supplier/add', views.add_pen_supplier, name='pen-supplier-add')
]
