# example/views.py
import os
import requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings 
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect

APPS_FOLDER = os.path.join(settings.BASE_DIR, 'applications')
# REPOS_BASE_URL = 'https://jihulab.com/anyangmvp/box/-/raw/main/'
REPOS_BASE_URL = 'https://raw.githubusercontent.com/anyangmvp/box/main/'


def index(request):
    return render(request, 'index.html')

@require_http_methods(["GET"])
def listapks(request):
    files = os.listdir(APPS_FOLDER)
    apk_files = [
        {"name": file, "url": f"/applications/{file}"} 
        for file in files if file.endswith(".apk")
    ]
    return JsonResponse(apk_files, safe=False)


@require_http_methods(["GET"])
def goto_repos(request, goto):
    gotoList = ['set', 'list', 'hd', 'hd1', 'hd2']
    if goto in gotoList:
        url = REPOS_BASE_URL + f'repositories/{goto}.json'
        try:
            response = requests.get(url)
            return HttpResponse(response.text)
        except:
            return HttpResponse("获取配置信息失败，请重试！", status=500)
    else:
        return HttpResponseRedirect('/')
    

@require_http_methods(["GET"])
def fuli(request):
    url = os.getenv("FULI_URL")
    html = f"""
        <h2>注意:线路来源于网络,并已将其保存至剪贴板,谢谢!</h2>
        {url}
        <hr><script>navigator.clipboard.writeText("{url}");</script>
    """
    return HttpResponse(html)