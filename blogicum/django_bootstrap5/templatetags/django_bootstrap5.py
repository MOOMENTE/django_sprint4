from django import forms, template
from django.forms.utils import flatatt
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def bootstrap_button(content, button_type="submit", **attrs):
    css_class = attrs.pop("class", "btn btn-primary")
    if "btn" not in css_class.split():
        css_class = f"btn {css_class}".strip()

    attrs_fragment = flatatt({k: v for k, v in attrs.items() if v is not None})
    return format_html(
        '<button type="{button_type}" class="{css}"{attrs}>{content}</button>',
        button_type=button_type,
        css=css_class,
        attrs=attrs_fragment,
        content=content,
    )


def _render_errors(errors):
    if not errors:
        return ""
    return format_html_join(
        "",
        '<div class="invalid-feedback d-block">{}</div>',
        ((error,) for error in errors),
    )


def _render_help(help_text):
    if not help_text:
        return ""
    return format_html('<div class="form-text">{}</div>', help_text)


def _non_field_alert(errors):
    if not errors:
        return ""
    content = format_html_join("", "{}", ((error,) for error in errors))
    return format_html(
        '<div class="alert alert-danger" role="alert">{}</div>',
        content,
    )


def _base_input_class(widget):
    if isinstance(widget, forms.CheckboxInput):
        return "form-check-input"
    if isinstance(widget, (forms.Select, forms.SelectMultiple)):
        return "form-select"
    return "form-control"


def _render_field(field, extra_class: str) -> str:
    widget = field.field.widget
    base_class = _base_input_class(widget)
    class_parts = [widget.attrs.get("class"), base_class, extra_class]
    if field.errors:
        class_parts.append("is-invalid")
    css_classes = " ".join(part for part in class_parts if part).strip()

    widget_attrs = {"class": css_classes}
    is_checkbox = isinstance(widget, forms.CheckboxInput)
    label_class = "form-check-label" if is_checkbox else "form-label"
    wrapper_class = "form-check mb-3" if is_checkbox else "mb-3"

    field_html = field.as_widget(attrs=widget_attrs)
    label_html = (
        field.label_tag(attrs={"class": label_class}) if field.label else ""
    )
    errors_html = _render_errors(field.errors)
    help_html = _render_help(field.help_text)

    if is_checkbox:
        return format_html(
            '<div class="{wrapper}">{input}{label}{errors}{help}</div>',
            wrapper=wrapper_class,
            input=field_html,
            label=label_html,
            errors=errors_html,
            help=help_html,
        )

    return format_html(
        '<div class="{wrapper}">{label}{input}{errors}{help}</div>',
        wrapper=wrapper_class,
        label=label_html,
        input=field_html,
        errors=errors_html,
        help=help_html,
    )


@register.simple_tag
def bootstrap_form(form, **kwargs):
    if form is None:
        return ""

    hidden_inputs = "".join(str(field) for field in form.hidden_fields())
    fragments = [hidden_inputs]

    non_field_errors = form.non_field_errors()
    if non_field_errors:
        fragments.append(_non_field_alert(non_field_errors))

    extra_class = kwargs.get("field_class", "")
    for field in form.visible_fields():
        fragments.append(_render_field(field, extra_class))

    return mark_safe("".join(fragments))


@register.simple_tag
def bootstrap_css():
    href = static("css/bootstrap.min.css")
    return format_html('<link rel="stylesheet" href="{}">', href)


@register.simple_tag
def bootstrap_javascript():
    cdn_src = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/"
        "bootstrap.bundle.min.js"
    )
    integrity = (
        "sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+AMr0LRn5q+8nb"
        "t+1aWtrXKXW8em"
    )
    script_template = (
        '<script src="{src}" integrity="{integrity}" '
        'crossorigin="anonymous"></script>'
    )
    return format_html(script_template, src=cdn_src, integrity=integrity)
