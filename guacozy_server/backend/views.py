from django.shortcuts import render

def index(request):
    """Serve the React app's index.html"""
    return render(request, 'index.html')