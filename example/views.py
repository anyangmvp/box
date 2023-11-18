# example/views.py
import hashlib
import os
import requests
import json
import time
import re
import tempfile
from urllib.parse import urlparse, urlunparse
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


#Live Proxy
class Cache:
    def __init__(self, cache_time=3600, cache_dir=tempfile.gettempdir()):
        self.cache_time = cache_time
        self.cache_dir = cache_dir

    def get_cache_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.txt")

    def is_cache_valid(self, path):
        if not os.path.exists(path):
            return False
        modified_time = os.path.getmtime(path)
        current_time = time.time()
        return (current_time - modified_time) < self.cache_time

    def get(self, key):
        cache_path = self.get_cache_path(key)
        if self.is_cache_valid(cache_path):
            with open(cache_path, "r",encoding='utf-8') as file:
                return file.read()
        return None

    def put(self, key, value):
        cache_path = self.get_cache_path(key)
        with open(cache_path, "w",encoding='utf-8') as file:
            file.write(value)

def randomString(length):
    import random
    import string
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

global_api = os.getenv("LIVE_API_URL")
global_key = os.getenv("LIVE_API_KEY")

global_device_id = randomString(16)
global_hardware = "6th"
global_version = "20220608"
global_from_value = "20268"
global_vparams = {}
global_vSys = {}
global_vArr = {}

def curl_get(url):
    cache = Cache(900)
    token = cache.get("token")
    cId = cache.get("client_id")
    header = {
        "User-Agent": "okhttp/3.12.5",
        "Userid": cId,
        "Usertoken": token
    }
    try:
        response = requests.get(url, headers=header, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return "Error: " + str(e)

def curl_post(url, postdata, header):
    try:
        response = requests.post(url, data=postdata, headers=header, timeout=20)
        response.raise_for_status()
        print('\n',response.text,'\n')
        return response.text
    except requests.exceptions.RequestException as e:
        return "Error: " + str(e)

def getCode(Method, token, password, client_id):
    # Setting
    timestr = time.time()
    sign = hashlib.md5((global_from_value + global_key + str(int(timestr)) + Method + global_device_id).encode()).hexdigest()

    if token:
        global_vparams["client_id"] = client_id
        global_vparams["password"] = password
        global_vparams["token"] = token
    global_vparams["device_id"] = global_device_id
    global_vparams["hardware"] = global_hardware
    global_vparams["sn"] = global_device_id
    global_vparams["version"] = global_version

    global_vSys["from"] = global_from_value
    global_vSys["sign"] = sign
    global_vSys["time"] = int(timestr)
    global_vSys["version"] = "V1"

    global_vArr["method"] = Method
    global_vArr["system"] = global_vSys
    global_vArr["params"] = global_vparams

    return json.dumps(global_vArr)

def getLive(data):
    import re
    import urllib.parse
    matches = re.search(r'"hlsManifestUrl":"(.*?)"', data)
    if matches:
        api = matches.group(1)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Referer": "https://www.youtube.com/"
        }
        try:
            response = requests.get(api, headers=headers)
            response.raise_for_status()
            data = response.text
            playUrl = ''
            if "SUBTITLES" in data:
                playUrl = api
            else:
                matches = re.findall(r"(https.*m3u8.*)\n", data)
                playUrl = matches[-1]
            return playUrl
        except requests.exceptions.RequestException:
            pass
    return None

@require_http_methods(["GET"])
def liveProxy(request):
    m3u8 = request.GET.get('url', '')
    ts = request.GET.get('ts', '')

    cache = Cache(900)
    pz = cache.get('peizi')

    if not pz:
        header = {
            "User-Agent": "okhttp/3.12.5",
        }
        respbody = curl_post(global_api, getCode("1-1-2",None,None,None), header)
        respbody = json.loads(respbody)['data']['client']
        print('1 --\n', respbody)
        token = respbody['token']
        password = respbody['password']
        client_id = respbody['client_id']

        respbody = curl_post(global_api, getCode("1-1-3",token,password,client_id), header)
        respbody = json.loads(respbody)['data']['client']
        print('2 --\n', respbody)
        token = respbody['token']

        cache.put("token", token)
        cache.put("password", password)
        cache.put("client_id", client_id)

        respbody = curl_post(global_api, getCode("1-1-4",token,password,client_id), header)
        rCode = json.loads(respbody)
        print('3 --\n', rCode)
        list = ''

        cate = []
        for v in rCode['data']:
            cate.append(v['category'])

        cate = set(cate)
        cc = ""

        parseUrl = "http://"
        parseUrl += request.META['HTTP_HOST']
        parseUrl += request.META['PATH_INFO']

        for ct in cate:
            cc += ct + ",#genre#\n"
            for v in rCode['data']:
                if v['category'] == ct:
                    cc += v['name'] + ',' + parseUrl + "?url=" + v['url'] + "\n"

        response = HttpResponse(cc, content_type='text/json;charset=utf-8')
        cache.put("peizi", cc)
        return response
    elif ts:
        url = urlparse(global_api)
        real = url.scheme + "://" + url.hostname + ts
        data = curl_get(real)
        response = HttpResponse(content=data, content_type='application/vnd.apple.mpegurl')
        response['Content-Disposition'] = 'attachment; filename="playlist.m3u8"'
        response['Cache-Control'] = 'no-cache'
        return response
    elif m3u8:
        if 'youtube' in m3u8:
            data = curl_get(m3u8)
            getLive(data)
        else:
            parseUrl = "http://"
            parseUrl += request.META['HTTP_HOST'] + request.META['PATH_INFO']
            url = urlparse(global_api)
            real = url.scheme + "://" + url.hostname + m3u8
            data = curl_get(real)
            if not data:
                return
            parsed_url = urlparse(real)
            parent_dir_url = parsed_url._replace(path='/'.join(parsed_url.path.split('/')[:-1]))
            newurl = urlunparse(parent_dir_url)
            path = urlparse(newurl).path
            replacement = parseUrl + "?ts=" + path + '/\\1'
            datac = re.sub(r'(.+\.ts)', replacement, data)
            response = HttpResponse(content=datac, content_type='application/vnd.apple.mpegurl')
            response['Content-Disposition'] = 'attachment; filename="playlist.m3u8"'
            response['Cache-Control'] = 'no-cache'
            return response
    else:
        return HttpResponse(pz)
    
