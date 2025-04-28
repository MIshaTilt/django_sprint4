from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('posts/<int:id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(),
         name='category_posts'),
]
