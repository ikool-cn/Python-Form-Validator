#!/usr/bin/python
# coding=utf-8
import operator
import re
import sys
from functools import wraps
from inspect import getattr_static
import copy


class Validator():
    """
    python form data validation class
    """

    def __init__(self, auto_trim=True, lang="zh"):
        self.auto_trim = auto_trim
        self.lang = lang
        self.rules = []
        self.errors = []
        self.data_verified = {}

    def set_rules(self, rules):
        """
        set validate rules
        :param rules:
        :return:
        """
        assert type(rules) == dict, "the rules must be type of dict"
        self.rules = rules
        return self

    def validate(self, data_raw):
        """
        execute validate
        :param data_raw:
        :return:
        """
        assert type(data_raw) == dict, "the raw data must be type of dict"
        self.data_raw = data_raw
        self.data_copy = copy.deepcopy(data_raw)

        ret = self.__execute(self.data_copy, self.rules)
        if False == ret:
            return False
        if len(self.errors) > 0:
            return False
        self.data_verified = ret
        return True

    def get_data(self, key=None):
        """
        get verified data
        :param key:
        :return:
        """
        return self.data_verified.get(key) if key else self.data_verified

    def get_error(self):
        """
        get error string
        :return:
        """
        return "\n".join(self.errors)

    def __execute(self, data_raw, rules):
        data = {}
        for field, rule in rules.items():
            if not field: continue
            if type(rule) == list:
                if type(data_raw.get(field)) != list:
                    raise ValueError("%s must be list" % field)
                data[field] = []
                for item in data_raw[field]:
                    ret = self.__execute(item, rule[0])
                    if type(ret) == bool and False == ret:
                        return False
                    data[field].append(ret)
            elif type(rule) == dict:
                data[field] = self.__execute(data_raw.get(field, None), rule)
            elif type(rule) == str:
                _rule, _label, _tip = self.__parse_rules(rule)
                ret = self.__execute_rule(field, data_raw.get(field, None), _rule, _label, _tip)
                if type(ret) == bool and False == ret:
                    return False
                data[field] = ret
            else:
                raise ValueError("rule type %s is not support" % type(rule))
        return data

    def __parse_rules(self, rule):
        _rule, _label, _tip = ([], "", "")
        pos = rule.find("`")
        if pos == -1:
            _rule = rule.split("|")
        else:
            _rule, tag = rule[:pos].split("|"), rule[pos:].strip()
            if "``" in tag:
                _tip = tag.replace("`", "")
            elif "`" in tag:
                _label = tag.replace("`", "")
            else:
                pass
        return _rule, _label, _tip

    def __execute_rule(self, field, data, rules=[], label="", tip=""):
        if self.auto_trim:
            rules.insert(0, "trim")
        for rule in rules:
            rule = str(rule).strip()
            if not rule:
                continue
            raw_params = ""
            if ":" in rule:
                expand = rule.split(":")
                raw_params = expand[1]
                func, params = expand[0], expand[1].split(",")
                if func == "match":
                    params, raw_params = self.__get_refrence_data(raw_params)
            else:
                func, params = rule, []
            func = self.__parse_func_alias(func)
            if hasattr(self, func):
                fn = getattr(self, func)
                data = fn(data, *params)
                if type(data) == bool and False == data:
                    if not tip:
                        label = label if label else field
                        error_tpl = ErrorTemplates.get(self.lang, func)
                        format_param_count = error_tpl.count("%s")
                        if format_param_count == 2:
                            error_msg = error_tpl % (label, raw_params)
                        elif format_param_count == 1:
                            error_msg = error_tpl % label
                        else:
                            error_msg = error_tpl
                    else:
                        error_msg = tip
                    self.__set_error(error_msg)
                    return False
            else:
                raise AttributeError("%s.%s cannot be call" % (__class__, func))
        return data

    def __parse_func_alias(self, func):
        alias = {
            "in": "isin",
        }
        return alias.get(func, func)

    def __get_refrence_data(self, key):
        params = self.data_raw.get(key)
        label = key
        rule = self.rules.get(key)
        if type(rule) == str:
            _, label, _ = self.__parse_rules(rule)
        return [params], label if label else key

    def __set_error(self, error_msg):
        self.errors.append(error_msg)

    def __del__(self):
        try:
            self.data_raw.clear()
        except:
            pass
        try:
            self.data_copy.clear()
        except:
            pass
        try:
            self.data_verified.clear()
        except:
            pass

    ####################################################################
    #                           verify method                          #
    ####################################################################

    @staticmethod
    def required(var):
        """
        The specified field must exist
        :param var:
        :return:
        """
        return False if var is None else var

    @staticmethod
    def not_empty(var):
        """
        The specified field cannot be empty
        :param var:
        :return:
        """
        return False if not var else var

    @staticmethod
    def len(var, length):
        """
        The string length of the specified field must be the specified value
        :param var:
        :param length:
        :return:
        """
        if type(var) != str:
            return False
        try:
            length = int(length)
        except:
            return False
        return var if len(var) == length else False

    @staticmethod
    def minlen(var, length):
        """
        The string length of the specified field must be greater than or equal to the specified value
        :param var:
        :param length:
        :return:
        """
        if type(var) != str:
            return False
        try:
            length = int(length)
        except:
            return False
        return var if len(var) >= length else False

    @staticmethod
    def maxlen(var, length):
        """
        The string length of the specified field must be less than or equal to the specified value
        :param var:
        :param length:
        :return:
        """
        if type(var) != str:
            return False
        try:
            length = int(length)
        except:
            return False
        return var if len(var) <= length else False

    @staticmethod
    def width(var, length):
        """
        The string width of the specified field must be equal to the specified value
        Chinese is calculated according to 2 characters
        :param var:
        :param length:
        :return:
        """
        try:
            length = int(length)
        except:
            return False
        return var if __class__.__strwidth(var) == length else False

    @staticmethod
    def minwidth(var, length):
        """
        The string width of the specified field must be greater than or equal to the specified value
        Chinese is calculated according to 2 characters
        :param var:
        :param length:
        :return:
        """
        try:
            length = int(length)
        except:
            return False
        return var if __class__.__strwidth(var) >= length else False

    @staticmethod
    def maxwidth(var, length):
        """
        The string width of the specified field must be less than or equal to the specified value
        Chinese is calculated according to 2 characters
        :param var:
        :param length:
        :return:
        """
        try:
            length = int(length)
        except:
            return False
        return var if __class__.__strwidth(var) <= length else False

    @staticmethod
    def __strwidth(var):
        if type(var) != str:
            return 0
        n = len(var)
        for x in var:
            if ord(x) > 127:
                n = n + 1
        return n

    @staticmethod
    def gt(var, num):
        """
        The specified field value must be greater than num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.gt)

    @staticmethod
    def lt(var, num):
        """
        The specified field value must be less than num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.lt)

    @staticmethod
    def gte(var, num):
        """
        The specified field value must be greater than or equal to num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.ge)

    @staticmethod
    def lte(var, num):
        """
        The specified field value must be less than or equal to num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.le)

    @staticmethod
    def eq(var, num):
        """
        The specified field value must be equal to num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.eq)

    @staticmethod
    def ne(var, num):
        """
        The specified field value must not be equal to num
        :param var:
        :param num:
        :return:
        """
        return __class__.__compare_num(var, num, operator.ne)

    @staticmethod
    def __compare_num(var, num, _operator):
        if type(var) == str:
            var = __class__.__str_to_num(var)
        if type(num) == str:
            num = __class__.__str_to_num(num)
        if type(var) not in (int, float) or type(num) not in (int, float):
            return False
        return var if _operator(var, num) else False

    @staticmethod
    def __str_to_num(var: str):
        if "." in var:
            try:
                return float(var)
            except Exception:
                return False
        else:
            try:
                return int(var)
            except Exception:
                return False

    @staticmethod
    def isin(var, *args):
        """
        The specified field value must be in the specified value
        :param var:
        :param args:
        :return:
        """
        return var if str(var) in args else False

    @staticmethod
    def nin(var, *args):
        """
        The specified field value must be not in the specified value
        :param var:
        :param args:
        :return:
        """
        return var if str(var) not in args else False

    @staticmethod
    def match(var1, var2):
        """
        The values of the two fields must be equal
        :param var1:
        :param var2:
        :return:
        """
        return var1 if var1 == var2 else False

    @staticmethod
    def is_mobile(var):
        """
        The specified field value must be Chinese mobile
        :param var:
        :return:
        """
        return str(var) if re.match("^1[3-9][0-9]{9}$", str(var)) else False

    @staticmethod
    def is_email(var):
        """
        The specified field value must be email
        :param var:
        :return:
        """
        return str(var) if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", str(var)) else False

    @staticmethod
    def is_idcard(var):
        """
        The specified field value must be Chinese idcard
        :param var:
        :return:
        """
        return str(var) if re.match(
            "(^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$)|(^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}$)",
            str(var)) else False

    @staticmethod
    def is_ip(var):
        """
        The specified field value must be ipv4 address
        :param var:
        :return:
        """
        return str(var) if re.match("^((\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.){4}$", str(var) + ".") else False

    @staticmethod
    def is_url(var):
        """
        The specified field value must be url
        :param var:
        :return:
        """
        return str(var) if re.match("^(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]$", str(var)) else False

    @staticmethod
    def is_list(var):
        """
        The specified field value must be list
        :param var:
        :return:
        """
        return var if type(var) == list else False

    @staticmethod
    def is_dict(var):
        """
        The specified field value must be dict
        :param var:
        :return:
        """
        return var if type(var) == dict else False

    @staticmethod
    def is_alpha(var):
        """
        The specified field value must be alpha
        :param var:
        :return:
        """
        return str(var) if re.match("^([a-z])+$", str(var), re.IGNORECASE) else False

    @staticmethod
    def is_alpha_num(var):
        """
        The specified field value must be alpha or num
        :param var:
        :return:
        """
        return str(var) if re.match("^([a-z0-9])+$", str(var), re.IGNORECASE) else False

    @staticmethod
    def is_alpha_dash_num(var):
        """
        The specified field value must be alpha or num or -_
        :param var:
        :return:
        """
        return str(var) if re.match("^([a-z0-9_-])+$", str(var), re.IGNORECASE) else False

    @staticmethod
    def is_zh(var):
        """
        The specified field value must be Chinese characters
        :param var:
        :return:
        """
        return str(var) if re.match("^([\u4E00-\u9FA5])+$", str(var)) else False

    ####################################################################
    #                          filter method                           #
    ####################################################################

    @staticmethod
    def trim(var):
        """
        Trim str
        :param var:
        :return:
        """
        return var.strip() if type(var) == str else var

    @staticmethod
    def int(var):
        """
        Convert var to int
        :param var:
        :return:
        """
        try:
            return int(var)
        except Exception:
            try:
                return int(float(var))
            except Exception:
                return 0

    @staticmethod
    def float(var):
        """
        Convert var to float
        :param var:
        :return:
        """
        try:
            return float(var)
        except Exception:
            return 0

    @staticmethod
    def str(var):
        """
        Convert var to str
        :param var:
        :return:
        """
        return str(var) if var or var == 0 else ""

    @staticmethod
    def upper(var):
        """
        Convert characters to uppercase
        :param var:
        :return:
        """
        return str(var).upper()

    @staticmethod
    def lower(var):
        """
        Convert characters to lowercase
        :param var:
        :return:
        """
        return str(var).lower()

    @staticmethod
    def filter_mb4(var):
        """
        Filter characters above 4 bytes
        :param var:
        :return:
        """
        return ''.join(c for c in var if ord(c) <= 0xffff)

    @staticmethod
    def filer_emoji(var):
        """
        Filter emoji in characters
        :param var:
        :return:
        """
        RE_EMOJI = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return RE_EMOJI.sub("", str(var))

    @staticmethod
    def filer_xss(var):
        """
        Filter xss in characters
        :param var:
        :return:
        """
        return str(var) \
            .replace("&", "&amp;") \
            .replace(">", "&gt;") \
            .replace("<", "&lt;") \
            .replace("'", "&#39;") \
            .replace('"', "&#34;")

    ####################################################################
    #                    extend method decorator                       #
    ####################################################################

    @classmethod
    def extend(cls):
        """
        extend validator method
        for example:

        @Validator.extend(Validator)
        def is_username(var):
            return str(var) if re.match("^([a-z0-9_-])+$", str(var), re.IGNORECASE) else False

        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            if getattr_static(cls, func.__name__, None):
                msg = 'Error method name REPEAT, {} has exist'.format(func.__name__)
                raise NameError(msg)
            else:
                setattr(cls, func.__name__, staticmethod(wrapper))
            return func

        return decorator


class ErrorTemplates():
    @staticmethod
    def get(lang, key):
        template = __class__.templates.get(lang)
        if not template:
            template = __class__.templates.get("zh")
        return template.get(key, __class__.default_error)

    default_error = "%s格式错误"

    templates = {
        "zh": {
            "required": "%s不存在",
            "not_empty": "%s不能为空",
            "len": "%s长度必须为%s个字符",
            "minlen": "%s最小长度为%s个字符",
            "maxlen": "%s最大长度为%s个字符",
            "width": "%s宽度必须为%s个字符",
            "minwidth": "%s最小宽度为%s个字符",
            "maxwidth": "%s最大宽度为%s个字符",
            "gt": "%s必须大于%s",
            "lt": "%s必须小于%s",
            "gte": "%s必须大于等于%s",
            "lte": "%s必须小于等于%s",
            "eq": "%s必须等于%s",
            "ne": "%s不能等于%s",
            "isin": "%s只能是%s",
            "nin": "%s不能是%s",
            "match": "%s和%s必须一致",
            "is_mobile": "手机号格式错误",
            "is_email": "邮箱格式错误",
            "is_idcard": "身份证号格式错误",
            "is_ip": "IP地址错误",
            "is_url": "%s不是有效的URL地址",
            "is_list": "%s必须是数组",
            "is_dict": "%s必须是字典",
            "is_alpha": "%s必须是字母",
            "is_alpha_num": "%s必须是字母或者数字",
            "is_alpha_dash_num": "%s必须是字母、数字或者下划线",
            "is_zh": "%s必须是汉字",
        },
        # "en": {
        #     "required": "%s can not be empty",
        #     ...
        # }
    }
