from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from .models import User

import hashlib
# Create your views here.

def reg_view(request):
    #注册
    if request.method == 'GET':
        # GET 返回页面
        return render(request,'user/register.html')
    elif request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['password_1']
        pass2 = request.POST['password_2']

        # POST 处理提交数据
        #  1. 密码一致
        if pass1 != pass2:
            return HttpResponse('两次输入密码不一致！！！')

        # 哈希算法 - 给定明文  计算出一段定长的  不可逆的值  md5  sha-256
        # 特点
        # 1. 定长输出 ： 不管明文输入长度多少  哈希值定长  md5 - 32位 16进制  【解释密码设置32】
        # 2. 不可逆 ：无法反向计算出 对应 的 明文
        # 3. 雪崩效应 输入改变 输出改变
        # 场景 ： 1.密码处理    2.文件的完整性校验
        # 如何使用 方法调用
        m = hashlib.md5()
        m.update(pass1.encode())  # encode()变成字节串
        pass1_hash = m.hexdigest()  # 生成哈希值

        #  2.当前用户名是否可用  检查是否注册
        old_user = User.objects.filter(username=username)
        if old_user:
            return HttpResponse('用户名已注册！！！')
        # 插入数据 【明文处理】
        try :
            user = User.objects.create(username=username,password=pass1_hash)
        except Exception as e:
            # 由于唯一索引 报错 重复插入 【唯一索引注意并发写入问题】
            print('--create user error %s' % (e))
            return HttpResponse('用户名已注册')
        return HttpResponse('注册成功！')
# 优化建议 ： 密码问题   创建语句问题
# 请求量大 User.objects.create 会报错 在username该字段 因为是唯一字段  可能由于并发注册问题 发生重复写入问题

        # 免登录一天 session  用户名  主键  存入 session
        request.session['username'] = username
        request.session['uid'] = user.id
        # TODO 修改session存储时间为1天   settings.py


        # return HttpResponse('注册成功')
        return HttpResponseRedirect('/index')


def login_view(request):
    if request.method == 'GET':
        # 获取登录页面
        # 检查登录状态  登陆过 显示已登录
        # 先检查session
        if request.session.get('username') and request.session.get('uid'):
            # return HttpResponse('已登录')
            return HttpResponseRedirect('/index')
        # 检查cookie

        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            # 回写到session中
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            # return HttpResponse('已登录')
            return HttpResponseRedirect('/index')
        # GET 返回页面
        return render(request,'user/login.html')
    elif request.method == 'POST':
        # 获得数据
        username = request.POST['username']
        password = request.POST['password']

        # 查询  是否有此人
        # username 是唯一索引
        try:
            user = User.objects.get(username=username) # 找不到 肯定没有
        except Exception as e:
            print('--login user error %s' % (e))
            return HttpResponse('用户名或者密码错误！！！')

        # 比对密码  因为哈希不可逆 所以从新生成哈希  用哈希数值进行比对
        m = hashlib.md5()
        m.update(password.encode())
        if m.hexdigest() != user.password:
            return HttpResponse('用户名或密码错误')

        # 记录会话状态
        # 免登录一天 session  用户名  主键  存入 session
        request.session['username'] = username
        request.session['uid'] = user.id

        # 判断有没有✔  通过检查浏览器响应分析 checkbox的状态 remember=on
        # #点选了->Cookies存储username,uid时间3天
        # resp = HttpResponse('--------success---------')
        resp = HttpResponseRedirect('/index')
        # print('request.POST:',request.POST)
        # request.POST: <QueryDict: {'username': ['zhenhao2'], 'password': ['123'], 'remember': ['on']}>

        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600 * 24 * 3)
            resp.set_cookie('uid', user.id, 3600 * 24 * 3)

        return resp

# 退出
def logout_view(request):
    # 删除session
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']

    # 检查cookie  删除cookie需要一个响应对象
    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.session:
        resp.delete_cookie('uid')
    return resp