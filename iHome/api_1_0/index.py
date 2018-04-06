# -*- coding:utf-8 -*-

from . import api


@api.route('/', methods=['GET', 'POST'])
def index():
    return 'index'