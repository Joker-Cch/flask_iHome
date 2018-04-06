# -*- coding:utf-8 -*-

from iHome import constants
from . import api
from iHome import redis_store
from iHome.utils.response_code import RET
from iHome.utils.captcha.captcha import captcha
from flask import request, jsonify, abort, current_app, make_response


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
