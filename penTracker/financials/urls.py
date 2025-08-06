from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('expenses/', views.expense_list, name='expense-list'),
    path('<int:pk>/edit/', views.edit_expense, name='expense-edit'),
    path('<int:pk>/delete/', views.delete_expense, name='expense-delete'),
    path('add/', views.add_expense, name='expense-add'),

    path('sales/', views.sale_list, name='sale-list'),
    path('record-sale/<int:pen_pk>/', views.record_sale, name='sale-record'),
    path('sales/<int:pk>/edit/', views.edit_sale, name='sale-edit'),
    path('sales/<int:pk>/delete/', views.delete_sale, name='sale-delete'),
]
