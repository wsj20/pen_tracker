from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense-list'),
    path('add/', views.add_expense, name='expense-add'),
    path('<int:pk>/edit/', views.edit_expense, name='expense-edit'),
    path('<int:pk>/delete/', views.delete_expense, name='expense-delete'),
    path('record-sale/<int:pen_pk>/', views.record_sale, name='sale-record'),
    path('sales/', views.sale_list, name='sale-list'),
]
