from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/', views.predict, name='predict'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    
    path('api/predictions/', views.get_predictions, name='get_predictions'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/earthquake/delete/<int:pk>/', views.delete_earthquake, name='delete_earthquake'),
    path('admin/prediction/delete/<int:pk>/', views.delete_prediction, name='delete_prediction'),
    
]