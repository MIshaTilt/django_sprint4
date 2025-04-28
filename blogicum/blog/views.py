from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Post, Category


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


class PostsListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Post
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 5
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
