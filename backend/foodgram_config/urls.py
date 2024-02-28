from django.contrib import admin
from django.urls import include, path
#vk/api/
urlpatterns = (
    path('admin/', admin.site.urls),
    path('api/', include('foodgram_api.urls', namespace='api')),
)
