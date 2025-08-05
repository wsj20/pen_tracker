from django.urls import path
from . import views

urlpatterns = [
    path('', views.pen_list, name='pen-list'),
    path('add/', views.add_pen, name='pen-add'),
    path('models/add/', views.add_pen_model, name='pen-model-add'),
    path('supplier/add/', views.add_pen_supplier, name='pen-supplier-add'),
    path('<int:pk>/', views.pen_detail, name='pen-detail'),
    path('<int:pk>/edit/', views.edit_pen, name='pen-edit'),
    path('<int:pk>/delete/', views.delete_pen, name='pen-delete'),
    path('parts/', views.part_list, name='part-list'),
    path('parts/add/', views.add_part, name='part-add'),
    path('parts/<int:pk>/edit/', views.edit_part, name='part-edit'),
    path('parts/<int:pk>/delete/', views.delete_part, name='part-delete'),
    path('usage/<int:pk>/delete/', views.delete_part_usage, name='part-usage-delete'),
]