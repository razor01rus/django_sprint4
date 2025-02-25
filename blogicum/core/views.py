from django.shortcuts import render # type: ignore


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию; 
    # выводить её в шаблон пользовательской страницы 404 мы не станем.
    return render(request, 'pages/404.html', status=404) 

def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

def server_error(request):
    return render(request, 'pages/500.html', status=500)  