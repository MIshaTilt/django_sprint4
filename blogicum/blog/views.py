from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DetailView, UpdateView
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

class CommentListView(ListView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    
class CommentCreateView(CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    success_url = reverse_lazy('birthday:list')




class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'blog/profile.html'
    context_object_name = 'profile'  # Имя переменной в шаблоне
    
    def get_object(self, queryset=None):
        username = self.kwargs['username']  # Match the URL parameter
        print(username)
        return get_object_or_404(get_user_model(), username=username)
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Запрашиваем все поздравления для выбранного дня рождения.
        context['page_obj'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            Post.objects.filter(author=self.object).select_related('author')
        )
        return context 
    
    
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = 'blog/user.html'
    context_object_name = 'profile'  # Имя переменной в шаблоне
    fields = ['username', 'first_name', 'last_name', 'email']  # Add this line with fields you want editable
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        # Используем reverse_lazy с именем URL 'profile' и текущим username
        return reverse_lazy('blog:profile', kwargs={'username': self.object.username})




class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:post_list')  # Default redirect to post list

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('blog:index')
    


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'  # Укажите ваш шаблон
    context_object_name = 'post'  # Имя переменной в шаблоне

    def get_object(self, queryset=None):
        # Получаем объект публикации по первичному ключу (pk)
        post = get_object_or_404(Post, pk=self.kwargs['id'])

        # Текущее время
        now = timezone.now()

        # Проверяем условия:
        # 1. Дата публикации не позже текущего времени
        # 2. Публикация опубликована
        # 3. Категория публикации опубликована
        if (
            post.pub_date > now
            or not post.is_published
            or not post.category.is_published
        ):
            # Если какое-либо условие не выполняется, возвращаем 404
            raise Http404("Публикация не найдена или недоступна.")

        return post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()

        return context


class PostsListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Post
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        # Текущее время
        now = timezone.now()

        # Фильтруем посты:
        # 1. Дата публикации не позже текущего времени
        # 2. Пост опубликован (is_published=True)
        # 3. Категория поста опубликована (category__is_published=True)
        return Post.objects.filter(
            pub_date__lte=now,  # Дата публикации не позже текущего времени
            is_published=True,  # Пост опубликован
            category__is_published=True  # Категория опубликована
        ).order_by('-pub_date')  # Сортируем по дате публикации (новые сначала)


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'  # Укажите ваш шаблон
    context_object_name = 'post_list'  # Имя переменной в шаблоне

    def get_queryset(self):
        # Получаем slug категории из URL
        category_slug = self.kwargs['slug']

        # Получаем категорию или возвращаем 404, если она не опубликована
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True  # Проверяем, что категория опубликована
        )

        # Текущее время
        now = timezone.now()

        # Фильтруем посты:
        # 1. Принадлежат выбранной категории
        # 2. Дата публикации не позже текущего времени
        # 3. Пост опубликован
        return Post.objects.filter(
            category=category,
            pub_date__lte=now,
            is_published=True
        ).order_by('-pub_date')  # Сортируем по дате публикации (новые сначала)

    def get_context_data(self, **kwargs):
        # Добавляем категорию в контекст шаблона
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True
        )
        return context
