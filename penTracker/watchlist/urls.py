from django.urls import path
from . import views

urlpatterns = [
    path('', views.watchlist_list, name='watchlist-list'),
    path('add/', views.add_watchlist_item, name='watchlist-add'),
    path('<int:pk>/', views.watchlist_detail, name='watchlist-detail'),
    path('<int:pk>/delete/', views.delete_watchlist_item, name='watchlist-delete'),
]
