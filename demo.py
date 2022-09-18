#!/usr/bin/python
# coding=utf-8

from helper.validator import Validator
import re

if __name__ == "__main__":

    post = {
        "username": "allen",
        "password": "123456",
        "grade": {
            "grade_name": "grade_3",
            "clsss": 308,
        },
        "education": [
            {
                "name": "希望小学123",
                "address": "朝阳路0001号"
            },
            {
                "name": "实验中学123",
                "address": "人民路002号"
            }
        ]
    }
    rules = {
        'username': 'required|trim|maxlen:10| `用户名`',
        'password': 'required|maxlen:8 `密码`',
        'grade': {
            'grade_name': 'required|str `年级`',
            'clsss': 'required|int|gt:0 `班级`',
        },
        'education': [
            {
                "name": "required|minlen:5",
                "address": "required|minlen:10"
            }
        ]
    }

    v = Validator()
    if v.set_rules(rules).validate(post):
        print(v.get_data())
    else:
        print(v.get_error())
        # address最小长度为10个字符
