from django.shortcuts import render

def visualization_page(request):
    context = {}
    return render(request, 'index.html', context)