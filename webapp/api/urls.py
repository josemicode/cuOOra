from django.urls import path, include
from rest_framework import routers
from api.views import BoardViewSet
# Routers provide an easy way of automatically determining the URL conf.

router = routers.DefaultRouter()
router.register(r'boards', BoardViewSet, basename='boards')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]