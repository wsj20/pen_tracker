from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense-list'),
    path('add/', views.add_expense, name='expense-add'),
]
