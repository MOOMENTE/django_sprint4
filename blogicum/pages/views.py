from django.shortcuts import render

# Кастомные обработчики ошибок


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=403)


def csrf_failure(request, reason=''):
    # Передаём причину сбоя в шаблон, чтобы было легче отладить
    context = {'reason': reason}
    response = render(request, 'pages/403csrf.html', context=context)
    response.status_code = 403
    return response
