from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('posts/<int:id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('category/<slug:slug>/', views.CategoryPostListView.as_view(),
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('profile/<slug:username>', views.UserDetailView.as_view(), 
         name='profile'),
    path('profile/edit/', views.UserUpdateView.as_view(), 
         name='edit_profile')
]
