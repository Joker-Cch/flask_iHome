# -*- coding:utf-8 -*-
# 提供个人中心数据

from . import api
from iHome import db, constants
from iHome.models import User
from iHome.utils.response_code import RET
from iHome.utils.image_storage import upload_image
from flask import session, current_app, jsonify, request


@api.route('/users')
def get_user_info():
    """提供用户个人信息
    0. TODO 先判断用户是否登录
    1.获取用户id (user_id)
    2.查询该登录用户的user信息
    3.构造响应数据
    4.响应数据
    """

    # 1.获取用户id (user_id)
    user_id = session.get('user_id')

    # 2.查询该登录用户的user信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 3.构造响应数据
    response_data = user.to_dict()

    # 4.响应数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_data)


@api.route('/users/avatar', methods=['POST'])
def upload_avatar():
    """提供用户头像上传
    0. TODO 先判断用户是否登录
    1.接受请求参数:avatar对应的图片数据，并校验
    2.调用上传图片的工具方法
    3.存储图片的key到user.avatar_url属性中
    4.响应上传结果，在结果中传入avatar_url，方便用户上传完成后立即刷新头像
    """

    # 1.接受请求参数:avatar对应的图片数据，并校验
    try:
        image_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='头像参数错误')

    # 2.调用上传图片的工具方法
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 3.存储图片的key到user.avatar_url属性中
    # 获取登录用户的user_id
    user_id = session.get('user_id')
    # 查询登录用户对象
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')
    # 给登录用户模型属性赋新值
    user.avatar_url = key
    # 将新值保存的数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储用户头像地址失败')

    # 4.响应上传结果，在结果中传入avatar_url，方便用户上传完成后立即刷新头像
    # 拼接访问头像的全路径
    # http://oyucyko3w.bkt.clouddn.com/FtEAyyPRhUT8SU3f5DNPeejBjMV5
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传头像成功', data=avatar_url)


@api.route('/users/name', methods=['PUT'])
def set_user_name():
    """修改用户名
    0. TODO 先判断用户是否登录
    1.接受用户传入的新名字， new_name
    2.判断参数是否为空
    3.查询当前登录用户
    4.将new_name赋值给当前的登录用户的name属性
    5.将新的数据写入到数据库
    6.响应结果
    """

    # 1.接受用户传入的新名字， new_name
    json_dict = request.json
    new_name = json_dict.get('name')

    # 2.判断参数是否为空
    if not new_name:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.查询当前登录用户
    user_id = session.get('user_id')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 4.将new_name赋值给当前的登录用户的name属性
    user.name = new_name

    # 5.将新的数据写入到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储用户名失败')

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='修改用户名成功')