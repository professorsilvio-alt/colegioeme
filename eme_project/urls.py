from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('painel-gestao-eme/', admin.site.urls),
    path('', include('core.urls')),
]
