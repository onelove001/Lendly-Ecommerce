from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from App.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("App/", include("App.urls")),
    path("Auth/", include("Auth.urls")),
    path("", home.as_view(), name="home"),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
