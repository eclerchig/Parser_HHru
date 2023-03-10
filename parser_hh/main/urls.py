from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('update_clouds_tokens', views.update_clouds_tokens, name='update_clouds_tokens'),
    path('update_charts', views.update_charts, name='update_charts')
]