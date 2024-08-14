from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from note.models import Note
from user.models import User

# Create your views here.
# 装饰器check_login
def check_login(fn):

    def wrap(request,*args,**kwargs):

        # 检查登录状态
        if 'username' not in request.session  or 'uid' not in request.session :
            # COOKIES
            c_username=request.COOKIES.get('username')
            c_uid=request.COOKIES.get('uid')
            if not c_username or not c_uid:
                # 302 重定向
                return HttpResponseRedirect('/user/login')   # 检查到当前没有人登录  跳转到 登录页面进行登录
            else:
                # 回写session
                request.session['username']=c_username
                request.session['uid']=c_uid
        return fn(request,*args,**kwargs)
    return wrap



# 登录校验的问题  复制代码？no no   使用 装饰器
@check_login
def add_note(request):
    if request.method == 'GET':
        return render(request,'note/add_note.html')
    elif request.method == 'POST':
        # 处理数据
        uid = request.session['uid']
        title = request.POST['title']
        content = request.POST['content']

        Note.objects.create(title=title,content=content,user_id=uid)

        return HttpResponse('添加笔记成功')


@check_login
def list_view(request):
    # 查找所有该作者所创建笔记的信息
    user = User.objects.get(username = request.session['username'])
    # notes = Note.objects.filter(user_id = user)
    notes = user.note_set.all()
    return render(request,'note/list_note.html',locals())
