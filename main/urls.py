from decimal import DefaultContext
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import PostViewSet, CategoryViewSet, category, edit
from .views import signin, logout, index, upload

router = DefaultRouter()
router.register('api/posts', PostViewSet, basename='posts')
router.register('api/categories', CategoryViewSet, basename='categories')

urlpatterns = router.urls + [
    path('signin/', signin, name="signin"),
    path('logout/', logout, name="logout"),
    path('upload/', upload, name="upload"),
    path('main/', index, name="index"),
    path('edit/<str:pk>/', edit, name="edit"),
    path('category/', category, name="category"),
]
