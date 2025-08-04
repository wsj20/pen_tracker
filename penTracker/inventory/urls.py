from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_inventory, name='sales-inventory')
]
