from rest_framework.routers import SimpleRouter

from apps.balance.views import BalanceViewSet

router = SimpleRouter()
router.register(r'balances', BalanceViewSet, basename='balance')
urlpatterns = router.urls
