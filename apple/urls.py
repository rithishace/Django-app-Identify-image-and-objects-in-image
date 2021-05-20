from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from imageclass.views import upload_image,view_result

urlpatterns = [
    path('admin/', admin.site.urls),
	path('',upload_image, name = 'home'),
	path('result/<int:pk>/', view_result, name = 'result'),
]


