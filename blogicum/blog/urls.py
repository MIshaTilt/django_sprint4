from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('posts/<int:post>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post>/edit_comment/<int:comment>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post>/delete_comment/<int:comment>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('category/<slug:slug>/', views.CategoryListView.as_view(),
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:post>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('profile/edit/', views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/', views.UserDetailView.as_view(),
         name='profile')

]
