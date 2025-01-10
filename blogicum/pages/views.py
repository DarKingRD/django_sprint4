from django.views.generic import TemplateView
from django.shortcuts import render


# Представление для страницы "О проекте"
class AboutView(TemplateView):
    template_name = "pages/about.html"


# Представление для страницы "Правила"
class RulesView(TemplateView):
    template_name = "pages/rules.html"


# Обработчик ошибки CSRF (403)
def csrf_failure(request, exception=None, reason=''):
    template = 'pages/403csrf.html'
    return render(request, template, status=403)


# Обработчик ошибки 404 (Страница не найдена)
def handler404(request, exception=None):
    template = 'pages/404.html'
    return render(request, template, status=404)


# Обработчик ошибки 500 (Ошибка сервера)
def handler500(request):
    template = 'pages/500.html'
    return render(request, template, status=500)
