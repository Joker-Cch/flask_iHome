# -*- coding:utf-8 -*-


from iHome import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from iHome import get_app
from iHome import models  # 在迁移之前，将模型导入一下


# 创建app
app = get_app('development')


# 创建脚本管理器对象
manager = Manager(app)

# 让app和db在迁移时建立关联
Migrate(app, db)
# 将数据库迁移脚本添加到脚本管理器
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # app.run()

    # print app.url_map

    manager.run()