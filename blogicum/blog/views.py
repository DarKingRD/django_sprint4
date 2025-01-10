from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Comment, Post


# Профиль пользователя
class ProfileView(generic.ListView):
    """
    Отображает профиль пользователя с его постами.
    Если пользователь просматривает свой профиль, отображаются все посты.
    Если другой пользователь, отображаются только опубликованные посты.
    """
    template_name = "blog/profile.html"
    context_object_name = "page_obj"  # Имя переменной контекста для пагинации
    paginate_by = 10  # Количество постов на странице

    def get_queryset(self):
        # Получаем пользователя, чей профиль просматривается
        self.profile = get_object_or_404(
            User, username=self.kwargs["username"])
        base_query = Post.objects.filter(author=self.profile)

        # Если пользователь просматривает свой профиль, показываем все посты
        if self.request.user == self.profile:
            return base_query.annotate(
                comment_count=Count("comments")
            ).order_by(
                "-pub_date"  # Сортировка по дате публикации (новые сначала)
            )

        # Для других пользователей показываем только опубликованные посты
        return (
            base_query.filter(
                Q(is_published=True)
                & Q(category__is_published=True)
                & Q(pub_date__lte=timezone.now())
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        # Добавляем профиль пользователя в контекст шаблона
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


# Редактирование профиля
class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    """
    Позволяет пользователю редактировать свой профиль.
    Доступно только авторизованным пользователям.
    """
    model = User
    form_class = UserProfileForm  # Форма для редактирования профиля
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        # Возвращает текущего пользователя для редактирования
        return self.request.user

    def get_success_url(self):
        # После успешного редактирования перенаправляем на профиль пользователя
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


# Список всех постов
class PostListView(generic.ListView):
    """
    Отображает список всех опубликованных постов с пагинацией.
    """
    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = 10  # Количество постов на странице

    def get_queryset(self):
        # Фильтруем только опубликованные посты
        return (
            Post.objects.filter(
                Q(is_published=True)
                & Q(category__is_published=True)
                & Q(pub_date__lte=timezone.now())
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


# Детали поста
class PostDetailView(generic.DetailView):
    """
    Отображает детали поста, включая комментарии.
    Если пост не опубликован или недоступен, возвращает 404.
    """
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        # Получаем пост и проверяем, доступен ли он для просмотра
        obj = super().get_object(queryset)
        if (
            not obj.is_published  # Пост не опубликован
            or not obj.category.is_published  # Категория не опубликована
            or obj.pub_date > timezone.now()  # Дата публикации в будущем
        ):
            if obj.author != self.request.user:  # Если это не автор поста
                raise Http404()  # Возвращаем 404
        return obj

    def get_context_data(self, **kwargs):
        # Добавляем форму комментария и список комментариев в контекст шаблона
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


# Создание поста
class PostCreateView(LoginRequiredMixin, generic.CreateView):
    """
    Позволяет авторизованным пользователям создавать новые посты.
    """
    model = Post
    form_class = PostForm  # Форма для создания поста
    template_name = "blog/create.html"

    def form_valid(self, form):
        # Устанавливаем автора поста перед сохранением
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # После успешного создания перенаправляем на профиль пользователя
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


# Редактирование поста
class PostEditView(LoginRequiredMixin, generic.UpdateView):
    """
    Позволяет авторизованным пользователям редактировать свои посты.
    """
    model = Post
    form_class = PostForm  # Форма для редактирования поста
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        # Получаем пост и проверяем, является ли пользователь его автором
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            return None  # Если нет, возвращаем None
        return obj

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, есть ли доступ к редактированию поста
        self.object = self.get_object()
        if self.object is None:
            # Если доступа нет, перенаправляем на страницу поста
            return redirect("blog:post_detail", post_id=kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # После успешного редактирования перенаправляем на страницу поста
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.id}
        )


# Удаление поста
class PostDeleteView(LoginRequiredMixin,
                     UserPassesTestMixin,
                     generic.DeleteView):
    """
    Позволяет авторизованным пользователям удалять свои посты.
    """
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        # Проверяем, является ли пользователь автором поста
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        # После успешного удаления перенаправляем на главную страницу
        return reverse("blog:index")


# Посты по категориям
class CategoryPostsView(generic.ListView):
    """
    Отображает список постов в определенной категории.
    """
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = 10  # Количество постов на странице

    def get_queryset(self):
        # Получаем категорию по slug и проверяем, опубликована ли она
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )

        # Фильтруем посты по категории и проверяем, опубликованы ли они
        return (
            Post.objects.filter(
                Q(category=self.category)
                & Q(is_published=True)
                & Q(category__is_published=True)
                & Q(pub_date__lte=timezone.now())
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        # Добавляем категорию в контекст шаблона
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


# Создание комментария
class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    """
    Позволяет авторизованным пользователям добавлять комментарии к постам.
    """
    model = Comment
    form_class = CommentForm  # Форма для создания комментария
    template_name = "includes/comments.html"

    def form_valid(self, form):
        # Устанавливаем пост и автора комментария перед сохранением
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # После успешного создания перенаправляем на страницу поста
        # с якорем на комментарий
        return (
            reverse("blog:post_detail", kwargs={
                    "post_id": self.kwargs["post_id"]})
            + f"#comment{self.object.id}"
        )


# Редактирование комментария
class CommentEditView(LoginRequiredMixin,
                      UserPassesTestMixin,
                      generic.UpdateView):
    """
    Позволяет авторизованным пользователям редактировать свои комментарии.
    """
    model = Comment
    form_class = CommentForm  # Форма для редактирования комментария
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        # Проверяем, является ли пользователь автором комментария
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        # После успешного редактирования перенаправляем на страницу поста
        # с якорем на комментарий
        return (
            reverse("blog:post_detail", kwargs={
                    "post_id": self.object.post.id})
            + f"#comment_{self.object.id}"
        )


# Удаление комментария
class CommentDeleteView(LoginRequiredMixin,
                        UserPassesTestMixin,
                        generic.DeleteView):
    """
    Позволяет авторизованным пользователям удалять свои комментарии.
    """
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        # Проверяем, является ли пользователь автором комментария
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        # После успешного удаления перенаправляем на страницу поста
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs["post_id"]}
        )
