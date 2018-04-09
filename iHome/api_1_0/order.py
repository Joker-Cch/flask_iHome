# -*- coding:utf-8 -*-

import datetime
from iHome import db
from iHome.api_1_0 import api
from iHome.models import House, Order
from iHome.utils.common import login_required
from iHome.utils.response_code import RET
from flask import request, jsonify, g, current_app


@api.route('/orders', methods=['POST'])
@login_required
def create_order():
    """创建、提交订单
    0.判断用户是否登录
    1.接受参数，house_id, 入住时间和离开时间
    2.校验参数，判断入住时间和离开是否符合逻辑，校验房屋是否存在
    3.判断当前房屋有没有被预定
    4.创建订单模型对象，并存储订单数据
    5.保存到数据库
    6.响应结果
    """
    # 1.接受参数，house_id, 入住时间和离开时间
    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_date_str = json_dict.get('start_date')
    end_date_str = json_dict.get('end_date')

    # 2.校验参数，判断入住时间和离开是否符合逻辑，校验房屋是否存在
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数不完整')

    # 校验房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'获取房屋失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg=u'房屋不存在')

    # 判断入住时间和离开是否符合逻辑
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date, Exception('入住时间有误')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=u'入住时间参数有误')

    # 3.判断当前房屋有没有被预定
    try:
        conflict_orders = Order.query.filter(Order.house_id == house_id,
                                             end_date > Order.begin_date,
                                             start_date < Order.end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询冲突订单失败')
    # 如果有值，说明要预订的房屋在该时间节点，已经在订单中，说明被预定
    if conflict_orders:
        return jsonify(errno=RET.DATAERR, errmsg=u'房屋已被预定')

    # 4.创建订单模型对象，并存储订单数据
    days = (end_date - start_date).days  # 计算时间段之间的天数
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = house.price * days

    # 5.保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=u'保存订单数据失败')

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg=u'OK')


@api.route('/orders', methods=['GET'])
@login_required
def get_order_list():
    """获取订单列表
    0. 判断用户是否登录
    1. 获取当前用户
    2. 获取当前用户所有订单列表
    3. 构造数据
    4. 响应数据
    """

    # 获取用户身份信息
    role = request.args.get('role')
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg=u'缺少必要参数')

    # 1. 获取当前用户
    user_id = g.user_id

    # 2. 获取当前用户所有订单列表
    try:
        if role == 'custom':
            orders = Order.query.filter(Order.user_id == user_id).all()
        else:
            # 查询该登录用户发布的房屋信息
            houses = House.query.filter(House.user_id == user_id).all()
            # 获取发布的房屋的ids
            house_ids = [house.id for house in houses]
            # 从订单中查询出订单中的house_id在house_ids
            orders = Order.query.filter(Order.house_id.in_(house_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'获取订单列表失败')

    # 3. 构造数据
    order_dict_list = []
    for order in orders:
        order_dict_list.append(order.to_dict())

    # 4. 响应数据
    return jsonify(errno=RET.OK, errmsg=u'OK', data=order_dict_list)








