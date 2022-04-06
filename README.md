这是BrainStorm系统的后端开发仓库.

主仓库: https://github.com/HK-vv/SE-BSsystem



### 使用说明书

在使用前，请向后端管理员申请获得`secret.json`文件，并将其放置在`BSsystem_backend/`目录下。没有此文件无法正常运行。此文件应当被保密, 请不要传播`secret.json`文件。

#### 指令运行

```bash
# 下载后端文件
git clone git@github.com:HK-vv/BSsystem_backend.git
cd BSsystem_backend 

# 安装必要包
pip install django
pip install requests

# 建立本地数据库
## 每次pull之后都要运行本段代码
## 运行此步报错尝试删除db.sqlite3和bsmodels/migrations并重新执行
python manage.py makemigrations bsmodels
python manage.py migrate

# 运行后端
python manage.py runserver 0.0.0.0:8080
```

输入以上指令后，即已运行后端，可以测试接口。

web端测试跳转，请将`dist`文件夹放置在`BSsystem_backend/`目录下，并保证主页路径为`BSsystem_backend/dist/index.html`后，打开[网址](http://localhost:8080/index.html)`http://localhost:8080/index.html`。

若无法运行，请联系管理员说明问题。

#### 创建超级管理员

输入以下指令

```
python manage.py createsuperuser
```

然后按照提示继续即可。

#### Django管理端

打开[网址](http://localhost:8080/admin/)`http://localhost:8080/admin/`，用超级管理员/管理员账号登录即可进入管理端。
