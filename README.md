# LajiHDKT
# 垃圾互动课堂

v2.0

互动课堂更新了检测是否帮别人登录扫码的逻辑，虽然做的很鸡肋。最重要的是这修复后的业务逻辑更是令人厌恶

签到系统的接口还有bug，用户信息接口存在bug，登陆页面的判断逻辑也有bug，可见这个系统到处都是bug，想完全解决基本只有重构的可能了。具体都有什么bug就不过多透漏了。

# 你需要

学习Python3

学习HTTP请求相关内容

学习jQuery中ajax的用法和数据处理逻辑基础

学习MVC和前后分离的结构原理

学习Nginx/Apache（反向代理/uWSGI SSL）

想优化的话可能还要学习更多关于jQuery和CORS的处理方式（前+后）

等等等等

# 它可以

让别人帮你签到，也可以一口气帮N多个人一起签

# 此代码

仅供学习使用

请勿滥用

自己动手，丰衣足食

# 额外注意

**此代码只是个小工具并且我也不是专门写前后端的，所以可能很多地方很不规范，请各位大哥有建议的还请发个PR。原本想前后分离的，但是jQ处理CORS时好像有问题，莫名其妙解析了OPTION却没有解析真正的POST的data，再加上想全部整合进一个文件，就干脆直接MVC好了。有什么解决办法的还请PR我哈，多谢**

* 扫一扫接口已经能用了，需要有自己的订阅号调起扫一扫接口。access key会自动管理（wechatpy依赖）
* log目录不能删除，否则会报错。建议还是保留日志，确保安全。日志记录了客户端IP，操作记录等
* Referer建议带上，具体连接需要自行使用Burpsuite去抓请求来找，以免服务端有日志记录
* Cookie同上
* POST请求中的data为学校id、学号、性别(需要按照固定一个字段)、课程ID，就不放啦
* 建议自行签发SSL证书，使用nginx做一层反向代理或者uWSGI
* **国内服务器需要备案，域名要备案，否则上述所有服务全部都无法使用**
* 实际使用的图片在本仓库**img**目录中，可以自行查看效果

# 额外福利

如果你是安卓手机，有个福利（我不确定iOS能不能用）。

如果要调试微信页面的前端的话，好像不是太方便，此时如果你是Android的话，很幸运你可以使用WeChat内置的浏览器（要求WeChat必须是大陆下载的，Play的不行）进行调试，前提是要打开手机的开发者设置中的USB调试

1. 连接手机，打开USB调试
2. 微信打开 http://debugx5.qq.com ，在第二个选项卡下把三个调试什么的打开，建议vConsole也开了吧
3. 电脑打开Google Chrome，打开地址 chrome://inspect/#devices  ，然后你会看到下边会显示出来你的设备中微信打开的页面
4. 然后点击Inspect，你就可以像Chrome F12一样调试了


# 依赖

建议服务器使用Fedora 29，较为推荐阿里云

需要安装Python3

需要flask requests wechatpy markdown依赖
