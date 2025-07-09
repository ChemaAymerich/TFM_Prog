from django.shortcuts import render

# Vista para servir la página principal
def home(request):
    return render(request, 'home.html')  # Asegúrate de tener 'home.html' en templates
