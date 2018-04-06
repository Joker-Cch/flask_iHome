# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# CSRF保护
from flask_wtf.csrf import CSRFProtect
# session在flask中的扩展包
from flask_session import Session


class Config(object):
    """加载配置"""

    # 开启调试模式
    DEBUG = True

    # 秘钥
    SECRET_KEY = 'AK0j4NSomJQKm8gD/917OniOIC8DEMQRP+xPBvGanEBieaADMBTA0EBTrJdAiXgU'

    # 配置mysql数据库:开发中使用真实IP
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.244.128:3306/flask_iHome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis数据库：开发中使用真实IP
    REDIS_HOST = '192.168.244.128'
    REDIS_PORT = 6379

    # 配置session数据存储到redis数据库
    SESSION_TYPE = 'redis'
    # 指定存储session数据的redis的位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名，意思是让session数据不以明文形式存储
    SESSION_USE_SIGNER = True
    # 設置session的会话的超时时长 ：一天
    PERMANENT_SESSION_LIFETIME = 3600 * 24


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)

# 创建连接到redis数据库的对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 创建脚本管理器对象
manager = Manager(app)

# 让app和db在迁移时建立关联
Migrate(app, db)
# 将数据库迁移脚本添加到甲苯管理器
manager.add_command('db', MigrateCommand)

# 开启CSRF保护
CSRFProtect(app)

# 使用session在flask扩展实现将session数据存储在redis
Session(app)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    manager.run()
