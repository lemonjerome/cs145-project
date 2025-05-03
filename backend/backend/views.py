# backend/views.py

from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

@method_decorator(never_cache, name='dispatch')
class FrontendAppView(TemplateView):
    template_name = 'index.html'
