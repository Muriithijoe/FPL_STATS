from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from . import views

urlpatterns=[
    url(r'^$',views.home,name='home'),
    url(r'^chart/',views.chart,name='chart'),
    url(r'^stats/',views.stats,name='stats')
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
