from rest_framework.routers import SimpleRouter

from apps.key.views import KeyViewSet

router = SimpleRouter()
router.register(r'keys', KeyViewSet, basename='key')
urlpatterns = router.urls
