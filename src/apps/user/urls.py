from rest_framework.routers import SimpleRouter

from apps.user.views import UserViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
