from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet, FollowViewSet, CreateDeleteSubscribe

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('users', UserViewSet, 'users')
router.register(r'users/subscriptions/', FollowViewSet, basename='subscriptions')
# router.register(r'users/(?P<id>\d+)/subscribe', FollowViewSet, basename='subscribe')


urlpatterns = (
    path('users/<int:user_id>/subscribe/',
           CreateDeleteSubscribe.as_view(), name='subscribe'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
)
# auth = [
#     path('login/', UserSignUpViewSet.as_view({'post': 'create'}),
#          name='login'),
#     path('logout/', UserAuthTokenAPIView.as_view(),
#          name='token'),
# ]

# urlpatterns = [
#     path('', include(router.urls)),
#     path('auth/', include('djoser.urls.token')),]
#     # path('auth/token/', include(auth)),]
# # http://localhost/api/users/
# # http://localhost/api/auth/token/logout/
# # http://localhost/api/auth/token/login/