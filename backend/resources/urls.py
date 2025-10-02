from django.urls import path
from resources import views

urlpatterns = [
    path('documents/', views.documents_view, name='documents'),
    path('reports/', views.reports_view, name='reports'),
    path('users/', views.users_management_view, name='users-management'),
]