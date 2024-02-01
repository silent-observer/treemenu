from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, "home.html", {})

def other(request, page):
    context = {"title": page}
    return render(request, "other.html", context)

def item(request):
    return render(request, "item.html", {})