from django.urls import path

from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('item1', views.item, name='item'),
    path('<slug:page>', views.other, name='other')
]