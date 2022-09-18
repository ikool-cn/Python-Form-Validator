## Python Form Data Validator

### 序言

#### 为什么要使用表单验证？
我们知道在日常的web开发中，仅仅依靠JS做一些基础的验证还不够，为了保证数据安全及合法性，后端也必须加一层规则验证，
如果要为每一个字段编写复杂的规则验证，那么开发效率又大大降低。因此封装了此验证库，可以大幅提高共同工作效率。
下面我们来看一个简单的例子：

目录结构：
```
├── helper
│   └── validator.py
└── test.py
```
代码如下：
```python
from helper.validator import Validator

if __name__ == "__main__":
    # 假设这是我们提交过来的数据
    post = {
        "username": "allen",
        "password": "123456",
        "repasswd": "123456",
        "age": "35",
        "sex": "1",
    }

    rules = {
        'username': 'required|maxlen:10',
        'password': 'required|minlen:4|maxlen:18 `密码`',
        'repasswd': 'required|match:password ``重复密码错误``',
        'age': 'required|int|gt:20|lte:35 `年龄`',
        'sex': 'required|in:0,1,2 `性别`',
        'bio': ''
    }

    v = Validator()
    if v.set_rules(rules).validate(post):
        print(v.get_data())
        # {'username': 'allen', 'password': '123456', 'repasswd': '123456', 'age': 35}
    else:
        print(v.get_error())
```
如果字段验证中有任何的规则不满足，将返回错误，是不是很简单？
您可能也注意到了有的规则后面带有反引号包裹，这是自定义字段名称和错误提示，稍后会介绍。

### 外部调用
Validator内置了很多静态方法，无需实例化，可以直接调用
```python
print(Validator.is_ip("192.168.1.256"))
# False

print(Validator.filer_emoji("Kiss 💋 me"))
# Kiss  me
```

### 模块实例化

```python
v = Validator(auto_trim=True, lang="zh")
```
实例化的时候可以携带2个参数：
+ auto_trim 自动去空格，默认值为True，当auto_trim为True时系统将自动在每一个字段验证规则前插入trim规则
+ lang 设置错误提示语言，默认值为zh

### 自定义错误提示
+ 默认情况下系统使用字段名作为label来生成错误提示
```python
post = {
    "username": "allen12345888",
}
rules = {
    'username': 'required|maxlen:10',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    #username最大长度为10个字符
```
+ 自定义字段名，使用单个反引号包裹
```python
post = {
    "username": "allen12345888",
}
rules = {
    'username': 'required|maxlen:10 `用户名`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    #用户名最大长度为10个字符
```
+ 自定义错误 使用双反引号包裹
```python
post = {
    "username": "allen12345888",
}
rules = {
    'username': 'required|maxlen:10 ``用户名错误``',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    #用户名错误
```

### 模块内置规则示例

#### 1、required
提交的数据中必须包含该字段，即：post.get(field) != None

```python
post = {
    "username": "allen",
}
rules = {
    'username': 'required|maxlen:10 `用户名`',
    'password': 'required|maxlen:10 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    #密码不存在
```

#### 2、trim
去除两端空格，如果我们在实例化的时候开启了auto_trim=True，则不用额外设置该规则
```python
post = {
    "username": "  allen  ",
    "password": "123456"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:10 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    #{'username': 'allen', 'password': '123456'}
else:
    print(v.get_error())
```

#### 3、not_empty
字段值非空
```python
post = {
    "username": "allen",
    "password": ""
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|not_empty `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 密码不能为空
```

#### 4、len
字段值必须是指定长度

```python
post = {
    "username": "allen",
    "password": "123456"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|len:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 密码长度必须为8个字符
```

#### 5、minlen
限制字段值的最小长度
```python
post = {
    "username": "allen",
    "password": "12345"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|minlen:6 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 密码最小长度为6个字符
```

#### 6、maxlen
限制字段值的最大长度

```python
post = {
    "username": "allen",
    "password": "123457890"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 密码最大长度为8个字符
```

#### 7、width
限制字段的宽度，一个中文算2个英文宽度
```python
post = {
    "username": "allen",
    "password": "123456",
    "nickname": "中文abc"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'nickname': 'required|width:6 `昵称`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 昵称宽度必须为6个字符
```

#### 8、minwidth
限制字段的最小宽度，一个中文算2个英文宽度
```python
post = {
    "username": "allen",
    "password": "123456",
    "nickname": "中文"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'nickname': 'required|minwidth:6 `昵称`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 昵称最小宽度为6个字符
```

#### 9、maxwidth
限制字段的最大宽度，一个中文算2个英文宽度
```python
post = {
    "username": "allen",
    "password": "123456",
    "nickname": "中文abc"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'nickname': 'required|maxwidth:6 `昵称`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 昵称最大宽度为6个字符
```

#### 10、gt
字段的值大于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "18"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|gt:18 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄必须大于18
```

#### 11、lt
字段的值小于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "35"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|lt:35 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄必须小于35
```

#### 12、gte
字段的值大于等于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "17"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|gte:18 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄必须大于等于18
```

#### 13、lte
字段的值小于等于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "36"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|lte:35 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄必须小于等于35
```

#### 14、eq
字段的值等于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "19"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|eq:18 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄必须等于18
```

#### 15、ne
字段的值不等于n
```python
post = {
    "username": "allen",
    "password": "123456",
    "age": "18"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': 'required|ne:18 `年龄`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 年龄不能等于18
```

#### 16、in
字段值必须在给定的列表里
```python
post = {
    "username": "allen",
    "password": "123456",
    "sex": "3"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'sex': 'required|in:0,1,2 `性别`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 性别只能是0,1,2
```
#### 17、nin
字段值不能在给定的列表里
```python
post = {
    "username": "allen",
    "password": "123456",
    "sex": "1"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'sex': 'required|nin:0,1,2 `性别`'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 性别只能是0,1,2
```

#### 18、match
两个字段的值相等，常用于密码和确认密码
```python
post = {
    "username": "allen",
    "password": "123456",
    "repassword": "12345",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'repassword': 'required|match:password `重复密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 重复密码和密码必须一致
```
#### 19、is_mobile
必须符合中国手机号规则
```python
post = {
    "username": "allen",
    "password": "123456",
    "mobile": "12345",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'mobile': 'required|is_mobile `手机号`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 手机号错误
```
#### 20、is_email
必须是正确的邮箱格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "email": "allen@gmail",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'email': 'required|is_email `邮箱`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 邮箱格式错误
```
#### 21、is_idcard
必须是有效的身份证格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "idcard": "42062119960203",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'idcard': 'required|is_idcard `身份证`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 身份证号格式错误
```
#### 22、is_ip
必须是正确的IPV4格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "ipaddress": "192.168.1.256",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'ipaddress': 'required|is_ip `IP地址`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # IP地址错误
```
#### 23、is_url
必须是有效的HTTP URL格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "url": "baidu.com",
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'url': 'required|is_url `个人主页`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 个人主页不是有效的URL地址
```
#### 24、is_list
必须是数组格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "hob": ""
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'hob': 'required|is_list',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # hob必须是数组
```
#### 25、is_dict
必须是字典格式
```python
post = {
    "username": "allen",
    "password": "123456",
    "hob": {}
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'hob': 'required|is_dict',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # hob必须是字典
```
#### 26、is_alpha
必须是字母
```python
post = {
    "username": "allen123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|is_alpha `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 用户名必须是字母
```
#### 27、is_alpha_num
必须是字母和数字
```python
post = {
    "username": "allen_123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|is_alpha_num `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 用户名必须是字母或者数字
```
#### 28、is_alpha_dash_num
必须是字母、数字、中划线、下划线
```python
post = {
    "username": "allen#123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|is_alpha_dash_num `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 用户名必须是字母、数字或者下划线
```
#### 29、is_zh
必须是汉字
```python
post = {
    "username": "中文123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|is_zh `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
else:
    print(v.get_error())
    # 用户名必须是汉字
```
#### 30、int
强转整形,错误的类型及转换失败的,转换结果为0
```python
post = {
    "username": "中文123",
    "password": "123456",
    "age": "3.25"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': "required|int"
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': '中文123', 'password': '123456', 'age': 3}
else:
    print(v.get_error())
```

#### 31、float
强转浮点数
```python
post = {
    "username": "中文123",
    "password": "123456",
    "age": "3.25"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'age': "required|float"
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': '中文123', 'password': '123456', 'age': 3.25}
else:
    print(v.get_error())
```

#### 32、str
强转字符串
```python
post = {
    "username": "中文123",
    "password": "123456",
    "dec": "3.25"
}
rules = {
    'username': 'required|trim|maxlen:10 `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'dec': "required|str"
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': '中文123', 'password': '123456', 'dec': '3.25'}
else:
    print(v.get_error())
```
#### 33、upper
强转大写
```python
post = {
    "username": "allen123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|upper `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'ALLEN123', 'password': '123456'}
else:
    print(v.get_error())
```
#### 34、lower
强转小写
```python
post = {
    "username": "Allen123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|lower `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'allen123', 'password': '123456'}
else:
    print(v.get_error())
```
#### 35、filter_mb4
过滤四字节以上字符
```python
post = {
    "username": "Allen💋123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|filter_mb4 `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'Allen123', 'password': '123456'}
else:
    print(v.get_error())
```
#### 36、filer_emoji
过滤emoji表情
```python
post = {
    "username": "Allen💋123",
    "password": "123456",
}
rules = {
    'username': 'required|trim|maxlen:10|filer_emoji `用户名`',
    'password': 'required|maxlen:8 `密码`',
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'Allen123', 'password': '123456'}
else:
    print(v.get_error())
```
#### 37、filer_xss
过滤xss攻击
```python
post = {
    "username": "allen",
    "password": "123456",
    "des": "<script>alert('sb')</script>"
}
rules = {
    'username': 'required|trim|maxlen:10| `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'des': 'required|filer_xss'
}
v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'allen', 'password': '123456', 'des': '&lt;script&gt;alert(&#39;sb&#39;)&lt;/script&gt;'}
else:
    print(v.get_error())
```

### 内置规则列表
```python
def required(var):pass
def not_empty(var):pass
def len(var, length):pass
def minlen(var, length):pass
def maxlen(var, length):pass
def width(var, length):pass
def minwidth(var, length):pass
def maxwidth(var, length):pass
def gt(var, num):pass
def lt(var, num):pass
def gte(var, num):pass
def lte(var, num):pass
def eq(var, num):pass
def ne(var, num):pass
def isin(var, *args):pass #alias in
def nin(var, *args):pass
def match(var1, var2):pass
def is_mobile(var):pass
def is_email(var):pass
def is_idcard(var):pass
def is_ip(var):pass
def is_url(var):pass
def is_list(var):pass
def is_dict(var):pass
def is_alpha(var):pass
def is_alpha_num(var):pass
def is_alpha_dash_num(var):pass
def is_zh(var):pass
def trim(var):pass
def int(var):pass
def float(var):pass
def str(var):pass
def upper(var):pass
def lower(var):pass
def filter_mb4(var):pass
def filer_emoji(var):pass
def filer_xss(var):pass
```

### 扩展验证方法
Validator提供了extend规则扩展功能，在一些复杂的验证场景我们可以自定义验证规则，只需要使用装饰器@Validator.extend()即可轻松实现。
代码示例：扩展一个match_qq验证规则
```python
post = {
        "username": "allen",
        "password": "123456",
        "qq": "asd12345678"
    }
rules = {
    'username': 'required|trim|maxlen:10| `用户名`',
    'password': 'required|maxlen:8 `密码`',
    'qq': 'required|match_qq `QQ号码`'
}

@Validator.extend()
def match_qq(qq):
    REG_QQ = re.compile("\d{4,11}")
    match = REG_QQ.search(qq)
    if match:
        return REG_QQ.search(qq).group()
    return False

v = Validator()
if v.set_rules(rules).validate(post):
    print(v.get_data())
    # {'username': 'allen', 'password': '123456', 'qq': '12345678'}
else:
    print(v.get_error())
```

### 对象及数组验证
支持一级对象及一维数组验证

```python
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
```