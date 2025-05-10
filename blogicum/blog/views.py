from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DetailView, UpdateView, DeleteView
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count

class CommentListView(ListView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']  # Получаем post_id из URL
        return get_object_or_404(Post, id=post_id)  # Используем поле id вместо post_id

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_object()  # Используем get_object для получения Post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.get_object().id})

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    
    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise Http404("Редактирование запрещено")
        return comment


    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.post.id})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    
    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user and not self.request.user.is_staff:
            raise Http404("Удаление запрещено")
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.post.id})


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'blog/profile.html'
    context_object_name = 'profile'  # Имя переменной в шаблоне
    
    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Если пользователь просматривает свой профиль
        if self.request.user == self.object:
            # Показываем ВСЕ посты, включая неопубликованные и будущие
            posts = Post.objects.filter(author=self.object)
        else:
            # Для других пользователей - только опубликованные посты с прошедшей датой
            posts = Post.objects.filter(
                author=self.object,
                is_published=True,
                pub_date__lte=now,
                category__is_published=True
            )
        
        # Сортировка и пагинация
        posts = posts.annotate(comment_count=Count('comment')).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        
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




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на страницу профиля текущего пользователя
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:post_list')  # Default redirect to post list

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Перенаправляем неавторизованного пользователя на страницу поста
            return HttpResponseRedirect(reverse('blog:post_detail', kwargs={'post_id': self.kwargs['pk']}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Убедимся, что только автор может редактировать пост
        if form.instance.author != self.request.user:
            return HttpResponseRedirect(reverse('blog:post_detail', kwargs={'post_id': self.kwargs['pk']}))
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на страницу профиля после успешного редактирования
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user and not self.request.user.is_staff:
            raise Http404("Удаление запрещено")
        return post

    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'  # Укажите ваш шаблон
    context_object_name = 'post'  # Имя переменной в шаблоне

    def get_object(self, queryset=None):
        # Получаем объект публикации по первичному ключу (pk)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        # Текущее время
        now = timezone.now()

        # Проверяем условия:
        # 1. Дата публикации не позже текущего времени
        # 2. Публикация опубликована
        # 3. Категория публикации опубликована
        if self.request.user != post.author:
            if (
                post.pub_date > now
                or not post.is_published
                or not post.category.is_published
            ):
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
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')  # Сортируем по дате публикации (новые сначала)

    

class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'  # Укажите ваш шаблон
    context_object_name = 'page_obj'  # Имя переменной в шаблоне
    paginate_by=10

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
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')  # Сортируем по дате публикации (новые сначала)

    def get_context_data(self, **kwargs):
        # Добавляем категорию в контекст шаблона
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True
        )
        return context
