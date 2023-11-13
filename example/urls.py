# example/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from  . import views

urlpatterns = [
    path('', views.index),
    path('listapks/', views.listapks, name='listapks'),
    path('18/', views.fuli, name='fuli'),
    path('<str:goto>/', views.goto_repos, name='goto'),
]

urlpatterns += static('/live/', document_root=settings.STATICFILES_DIRS[0])