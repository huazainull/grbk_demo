from flask import Flask,render_template,request,session,redirect,url_for,g

import config
from models import User,Article,Type,Commten,Message
from exits import db
from others import valid
app=Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# 模板页
@app.route('/')
def base():
    return  render_template('base.html')

# 首页
@app.route('/index/',methods=['POST','GET'])
@valid
def index():
    user=g.user
    types=user.types
    result={
        'types':types
    }
    return render_template('index.html',**result)

# 文章列表页
@app.route('/list/<id>/',methods=['GET'])
@valid
def list(id):
    if request.method=='GET':
        type=Type.query.filter(Type.id==id).first()
        res={
            'articles':type.articles
        }
        return render_template('list.html',**res)

# 留言功能
@app.route('/message/',methods=['GET','POST'])
@valid
def message():
    messages=Message.query.filter(Message.author_id==g.user_id)
    referer=request.headers.get('Referer')
    if request.method=='POST':
        content=request.form.get('content')
        mess=Message(
            content=content,
            author=g.user
        )
        db.session.add(mess)
        db.session.commit()
        return redirect(referer)

    return render_template('message.html',messages=messages)

# 文章详情页
@app.route('/detali/<a_id>',methods=['GET','POST'])
@valid
def detali(a_id):
    referer_url=request.headers.get('Referer')
    article = Article.query.filter(Article.id == a_id).first()
    coms=article.comments
    com_num=len(coms)
    if request.method=='GET':
        article_previous=Article.query.filter(Article.id==(int(a_id)+1)).first()
        article_next=Article.query.filter(Article.id==(int(a_id)-1)).first()
        res={
            'article':article,
            'article_previous': article_previous,
            'article_next': article_next,
            "coms":coms,
            'com_num':com_num
        }
        return render_template('detali.html',**res)

    if request.method=="POST":
        content=request.form.get('content')
        article=Article.query.filter(Article.id==a_id).first()
        author=g.user
        comment=Commten(
            content=content,
            article=article,
            author=author
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(referer_url)

# 注册功能
@app.route('/register/',methods=['POST','GET'])
def register():
    result=''
    if request.method=='POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        phone = request.form.get('phone')
        u=User.query.filter(User.phone==phone).first()
        if u:
            result="该手机号已存在请重新输入"
        else:
            if password1==password2:
                user=User(
                    username=username,
                    password=password2,
                    phone=phone
                )
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                result="密码不一致"
    return  render_template('register.html',result=result)

# 登录功能
@app.route('/login/',methods=['POST','GET'])
def login():
    msg=''
    if request.method=='POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user=User.query.filter(User.phone==phone).first()
        if user and user.check(password):
            session['user_id']=user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            msg='用户名密码错误'
            # return '用户名密码错误'
    return  render_template('login.html',msg=msg)

# 注销功能
@app.route('/logout/',methods=['POST','GET'])
def logout():
    # session.clear()
    del session['user_id']
    return redirect(url_for('login'))

# 添加文章
@app.route('/addArticle/',methods=['POST','GET'])
@valid
def addArticle():
    result={
        'types':g.user.types
    }

    if request.method=='POST':
        title = request.form.get('title')
        content = request.form.get('content')
        description = request.form.get('description')
        user=g.user
        type_id=request.form.get('types')
        type=Type.query.filter(Type.id==type_id).first()
        article=Article(
            title=title,
            content=content,
            author=user,
            type=type,
            description=description
        )
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('addArticle.html',**result)

# 添加文章类型
@app.route('/addType/',methods=['POST','GET'])
@valid
def addType():
    if request.method=='POST':
        title = request.form.get('title')
        description = request.form.get('description')
        author = g.user
        type=Type(title=title,description=description,author=author)

        db.session.add(type)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('addType.html')

# 点赞功能
@app.route('/changeNum/',methods=['POST','GET'])
def changeNum():
    if request.method=='GET':
        num=request.args.get('num')
        art_id = request.args.get('art_id')
        # print('num',num)
        # print('art_id',art_id)
        article = Article.query.filter(Article.id == art_id).first()
        article.zan_num=int(num)+1
        db.session.commit()
        return '数据库已更新'

# 搜索功能
from sqlalchemy import or_
@app.route('/seacher/',methods=['POST','GET'])
def seacher():
    if request.method=='POST':
        q=request.form.get('keyboard')
        condiction=or_(Article.content.contains(q),Article.description.contains(q),Article.title.contains(q))
        res={
            'articles':Article.query.filter(condiction)
        }
        return render_template('list.html',**res)


@app.route('/check/',methods=['POST','GET'])
def check():
    if request.method=='GET':
        phone=request.args.get('phone')
        pwd = request.args.get('pwd')
        user = User.query.filter(User.phone == phone).first()
        if user:
            if  user.check(pwd):
                return ""
            else:
                return "账号或密码错误，请核对再输入"
# 钩子函数，请求前调用
@app.before_request
def before_request():
    user_id=session.get('user_id')
    if user_id:
        user=User.query.filter(User.id==user_id).first()
        if user:
            g.user_id=user_id
            g.user=user
# 钩子函数 上下文处理器
@app.context_processor
def context_processor():
    if hasattr(g,'user'):
        types = g.user.types
        return {'user':g.user,
                'types': types
                }
    return {}

if __name__ == '__main__':
    app.run(debug=True)
