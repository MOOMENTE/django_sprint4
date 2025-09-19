from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

AUTHOR_NAME = "Юсупов Аюбджон"
AUTHOR_EMAIL = "aybjonju@gmail.com"


class StaticPageView(TemplateView):
    """Base class for simple informational pages."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("generated_at", datetime.now())
        return context


class AboutView(StaticPageView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"page_title": "О проекте", "author": AUTHOR_NAME})
        return context


class RulesView(StaticPageView):
    template_name = "pages/rules.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", "Правила площадки")
        return context


class ContactsView(StaticPageView):
    template_name = "pages/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Контакты",
                "primary_contact": AUTHOR_NAME,
                "email": AUTHOR_EMAIL,
            }
        )
        return context


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "pages/404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/500.html", status=500)


def permission_denied(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "pages/403.html", status=403)


def csrf_failure(request: HttpRequest, reason="") -> HttpResponse:
    context = {"reason": reason}
    return render(request, "pages/403csrf.html", context=context, status=403)
