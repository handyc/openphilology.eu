from django.shortcuts import render
from django.template import loader

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

def index(request):
    latest_work_list = "test"

    template = loader.get_template('editor/index.html')
    context = {
        'latest_work_list': latest_work_list,
    }
    return HttpResponse(template.render(context, request))

