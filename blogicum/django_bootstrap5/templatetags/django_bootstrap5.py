"""Minimal subset of template tags used in project templates.

This stub is provided so the test environment does not require the
third-party ``django_bootstrap5`` package.  The implementation covers only
what the templates in this repository rely on.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def bootstrap_css():
    """Return an empty string instead of relying on the real package."""
    return ""


@register.simple_tag
def bootstrap_button(*, button_type="submit", content="", **_kwargs):
    html = (
        f'<button type="{button_type}" class="btn btn-primary">'
        f"{content}</button>"
    )
    return mark_safe(html)


@register.simple_tag
def bootstrap_form(form, **_kwargs):
    """Render the form using the default ``as_p`` representation."""
    return mark_safe(form.as_p())
