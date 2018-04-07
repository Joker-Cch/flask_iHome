# -*- coding:utf-8 -*-
# 实现房屋模块接口

from . import api
from iHome.models import Area
from flask import current_app, jsonify
from iHome.utils.response_code import RET


@api.route('/areas')
def get_areas():
    '''提供城区信息
    1. 查询所有的城区信息
    2. 构造响应数据
    3. 响应结果
    '''

    # 1.查询所有的城区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询城区信息失败')

    # 2.构造响应数据
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg=u'OK', data=area_dict_list)
