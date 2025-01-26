from django.urls import path # type: ignore

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.page_not_found, name='page_not_found'),
]
