# -*- coding:utf-8 -*-

import re
import random
from iHome import constants
from iHome.utils.sms import CCP
from . import api
from iHome import redis_store
from iHome.utils.response_code import RET
from iHome.utils.captcha.captcha import captcha
from flask import request, jsonify, abort, current_app, make_response, json


@api.route('/image_code')
def get_image_code():
    """ 提供图片验证码
    1.接受请求，获取uuid
    2.生成图片验证码
    3.使用UUID存储图片验证码内容到redis
    4.返回图片验证码
    """

    # 1.接受请求，获取uuid
    uuid = request.args.get('uuid')
    last_uuid = request.args.get('last_uuid')
    if not uuid:
        abort(403)
        # return jsonify(errno=RET.PARAMERR, errmsg=u'缺少uuid')

    # 2.生成验证码:text是验证码的文字信息，image验证码的图片信息
    name, text, image = captcha.generate_captcha()
    # 将调试信息写入到?logs/logs
    # logging.debug('图片验证码文字信息：' + text)
    current_app.logger.debug('图片验证码文字信息:' + text)

    # 3.使用UUID存储图片验证码内容到redis
    try:
        if last_uuid:
            # 上次的uuid还存在，删除上次的uuid对应的记录
            redis_store.delete('ImageCode:' + last_uuid)

        # 保存本次需要记录的验证码数据
        redis_store.set('ImageCode:' + uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        # 将错误信息写入到?logs/logs
        # logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'保存验证码失败')

    # 4.返回图片验证码
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


@api.route('/sms_code', methods=['POST'])
def send_sms_code():
    """ 发送短信验证码
    1.接受参数：手机号，图片验证码，uuid
    2.判断参数是否缺少，并且要对手机号进行校验
    3.获取服务器存储的图片验证码，uuid作为key
    4.与客户端传入的图片验证码对比，如果对比成功
    5.发送短信给用户
    6.响应短信发送的结果
    """

    # 1.接受参数：手机号，图片验证码，uuid
    # data : 保存请求报文里面的原始的字符串，开发文档约定，客户端发送的是json字符串
    json_str = request.data
    json_dict = json.loads(json_str)

    mobile = json_dict.get('mobile')
    image_client = json_dict.get('imagecode')
    uuid = json_dict.get('uuid')

    # 2.判断参数是否缺少，并且要对手机号进行校验
    if not all([mobile, image_client, uuid]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'缺少参数')
    # 校验手机号码是否合法
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=u'号码格式错误')

    # 3.获取服务器存储的图片验证码，uuid作为key
    try:
        image_server = redis_store.get('ImageCode:' + uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询服务器验证码失败')

    # 判断是否为空或者过期
    if not image_server:
        return jsonify(errno=RET.NODATA, errmsg=u'验证码已失效')

    # 4.与客户端传入的图片验证码对比，如果对比不成功
    if image_server.lower() != image_client.lower():
        return jsonify(errno=RET.DATAERR, errmsg=u'验证码有误')

    # 5.生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('短信验证码为：' + sms_code)

    # 6.使用云通讯将短信验证码发送到注册用户手中
    # result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], '1')
    # if result != 1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')

    # 7.存储短信验证码到redis中:短信验证码在redis中的有效期一定要和短信验证码的提示信息一致
    try:
        redis_store.set('Mobile:' + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储短信验证码失败')

    # 8.响应短信发送的结果
    return jsonify(errno=RET.OK, errmsg='发送短信验证码成功')
