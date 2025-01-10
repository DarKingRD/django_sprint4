from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("blog.urls")),
    path('pages/', include("pages.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name="registration/registration_form.html",
            form_class=UserCreationForm,
            success_url=reverse_lazy("blog:index"),  # мб изменить ссылку
        ),
        name="registration",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Кастомные странички ошибок
handler404 = 'pages.views.handler404'
handler500 = 'pages.views.handler500'
handler403 = "pages.views.csrf_failure"
