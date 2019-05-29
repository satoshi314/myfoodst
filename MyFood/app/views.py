from django.shortcuts import get_object_or_404, redirect, render
from .models import Shop
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .forms import ShopForm
#from .forms import SearchForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import time
from tqdm import tqdm
import folium

def index(request):
    shops = Shop.objects.all().order_by('-id')
    return render(request, 'app/index.html', {'shops': shops})

def users_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'app/users_detail.html', {'user': user})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # ユーザーインスタンスを作成
        if form.is_valid():
            new_user = form.save() # ユーザーインスタンスを保存
            input_username = form.cleaned_data['username']
            input_password = form.cleaned_data['password1']
            # フォームの入力値で認証できればユーザーオブジェクト、できなければNoneを返す
            new_user = authenticate(username=input_username, password=input_password)
            # 認証成功時のみ、ユーザーをログインさせる
            if new_user is not None:
                # loginメソッドは、認証ができてなくてもログインさせることができる。→上のauthenticateで認証を実行する
                login(request, new_user)
                return redirect('app:users_detail', pk=new_user.pk)
    else:
        form = UserCreationForm()
    return render(request, 'app/signup.html', {'form': form})
    
    
    
@login_required  
def shops_new(request):
    if request.method == "POST":
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.user = request.user
            shop.save()      
            messages.success(request, "登録が完了しました！")                
#    return redirect('app:users_detail', pk=request.user.pk)
        return render(request,'app/success.html')
    else:
        form = ShopForm()
    return render(request, 'app/shops_new.html', {'form': form})

def go_search(request):    
#    form = SearchForm()
#    return render(request, 'app/shops_search.html', {'form': form})
    return render(request, 'app/shops_search.html')

def shops_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    return render(request, 'app/shops_detail.html', {'shop': shop})

@require_POST
def shops_delete(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    shop.delete()
    return redirect('app:users_detail', request.user.id)

def shops_search(request):
    i = 0
    address =""
    evaluate =""
    kuchikomi =""
    teikyu =""
    lunch_bud =""
    dinner_bud =""
    info =[]
    name =""
    geourl = 'http://www.geocoding.jp/api/'

    
    # URLから店名、住所、最寄り駅、ジャンル、評価、口コミ数、定休日、昼予算、夜予算を取得
#    url = 'https://tabelog.com/okayama/A3301/A330101/33001614/'

    url=request.GET.get('search_url')    
#    form=SearchForm(request.GET)
#    url =form.url
#    form_obj = form.save(commit=False)    
#    url=form_obj.url
    
    
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")


    name=soup.find(class_="display-name").getText().strip()  #strip で不要な空白を削除

    for info in soup.findAll("span",class_="linktree__parent-target-text"):
        i= i + 1
        if i == 1 :   #駅名
            station = re.split('駅',info.getText())[0]
        if i == 3 :   #1つ目のジャンル
            genre = info.getText()
        if i >3   :   #2つ目以降のジャンル
            genre = genre + "、" + info.getText()
        
    try:
        address=soup.find("p",class_="rstinfo-table__address").getText()
    except:
        address="住所情報なし"
    try:    
        evaluate=soup.find(class_="rdheader-rating__score-val-dtl").getText()
    except:
        evaluate=0
    try:    
        kuchikomi=soup.find(class_="num").getText()
    except:
        kuchikomi=0 
    try:    
        teikyu=soup.find(class_="rdheader-subinfo__closed-text").getText().strip()
    except :
        teikyu="定休情報なし"
    try:    
        lunch_bud=soup.find(class_="gly-b-lunch").getText()
    except:
        lunch_bud="ランチ情報なし"    
    try:
        dinner_bud=soup.find(class_="gly-b-dinner").getText()
    except :
        dinner_bud="ディナー情報なし"
 #  googleのAPIを利用し、住所を緯度経度に変換する。　
    payload = {'q': address}
    r = requests.get(geourl, params=payload)
    ret = BeautifulSoup(r.content,'lxml')
    if ret.find('error'):
        raise ValueError(f"Invalid address submitted. {address}")
    else:
 #  緯度経度の取得に成功したときの処理  
        lat =float(ret.find('lat').string)
        lon =float(ret.find('lng').string) 	
        
#    shop = get_object_or_404(Shop, pk=1)

#    shop=Shop.objects.create(
#    name = name,
#    evaluate=evaluate,
#    station=station,
#    genre=genre,
#    url =url,
#    coordinate=str(lat)+ "," + str(lon),
#    user =request.user,
#    )

#    shop = create(Shop)    

    shop=Shop       
    shop.name = name
    shop.evaluate=evaluate
    shop.station=station
    shop.genre=genre
    shop.url =url
    shop.coordinate=str(lat)+ "," + str(lon)
    shop.user =request.user
    print("【URL検索_実行結果】")
    print(shop.name)
    print(shop.evaluate)
    print(shop.station)
    print(shop.genre)
    print(shop.url)
    print(shop.coordinate)
    
#    initial_dict = {
#        'name' : name,
#        'evaluate' : evaluate
#    }
#     initial_dict= {
#     'name' : name,
#     'evaluatea :evaluate'
#     }
#    form = ShopForm(request.POST or None, initial = shop)
 #   return render(request, 'app/shops_new.html', {'shop': shop})
    
    form =ShopForm(instance=shop)

#    form.name=name
#    return render(request, 'app/search_result.html', {'shop': shop})
    return render(request, 'app/shops_new.html', {'form': form})