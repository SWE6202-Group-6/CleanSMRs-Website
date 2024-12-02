from django.shortcuts import render

# Create your views here.

def index(request):
    """Renders the index page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: A HTTP response rendering the index template.
    """
    return render(request, 'index.html')
