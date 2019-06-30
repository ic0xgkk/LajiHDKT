import flask
import logging
import time
import json
import requests
import wechatpy
import random
import markdown
import threading

logname = time.strftime("%Y%m%d%H%M%S", time.localtime())
logname = './log/lajihdkt-' + logname + '.log'
logging.basicConfig(filename=logname,
                    level=logging.DEBUG,
                    format='[%(levelname)s:%(asctime)s] %(message)s')
logging.warning("Server started")

users = [
    {
        "name": "名字",
        "referer": "Referer",
        "cookie": "Cookie，随便一个按照签到时的格式（长度）即可",
        "id": "学号"
    }
]


class WeChatJSAPI(object):
    __config = {
        "AppID": "微信AppID",
        "AppSecret": "AppSecret",
        "url": "/a/b", # 鉴权参数注入接口
        "index": "/", # 调起页面（index）
        "sig_url": "https://aaa.aaa.com/" # 调起页面的完整地址，签名用
    }

    def __init__(self):
        self.client = wechatpy.WeChatClient(self.__config['AppID'], self.__config['AppSecret'])

    def __get_ticket(self):
        t = self.client.jsapi.get_jsapi_ticket()
        return t

    def get_url(self):
        return self.__config['url']

    def get_index(self):
        return self.__config['index']

    def get_sig_url(self):
        return self.__config['sig_url']

    def get_jswxconfig(self):
        appId = self.__config['AppID']
        timestamp = str(int(time.time()))
        noncestr = self.__gen_rdstr()
        ticket = self.__get_ticket()
        url = self.__config['sig_url']
        signature = self.client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
        return {
            "appId": appId,
            "timestamp": timestamp,
            "nonceStr": noncestr,
            "signature": signature
        }

    def __gen_rdstr(self, length=16):
        if length >= 60:
            raise BaseException("随机串长度不允许超过60位")
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        for i in range(length):
            random_str += base_str[random.randint(0, len(base_str) - 1)]
        return random_str


class FlaskApp(object):
    def __init__(self, WX: WeChatJSAPI):
        self.full_table = ""
        self.Lock = 0
        self.Lock = threading.RLock()
        self.WXClient = WX
        self.app = flask.Flask(__name__)
        self.url_route()
        self.start()

    def start(self):
        self.app.run(host="127.0.0.1", port=3065, debug=False, threaded=True)

    def url_route(self):
        self.app.add_url_rule(self.WXClient.get_url(), 'wx_api', self.wxconfig_post, methods=['POST'])
        self.app.add_url_rule(self.WXClient.get_url(), 'sign_api', self.sign, methods=['GET'])
        self.app.add_url_rule(self.WXClient.get_index(), 'index', self.index, methods=['GET'])

    def index(self):
        html = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<title>调起中...</title>
</head>
<body>
<h1>正在调起扫一扫...</h1>
<br><br>
<strong>
    Ice Cream 2019
</strong>
<script src="https://填自己的CDN域名/jquery-3.4.0.min.js"></script>
<script src="https://res.wx.qq.com/open/js/jweixin-1.4.0.js"></script>
<script type="text/javascript">
  $.ajax({
      url: "https://aa.aaa.com/wwwwwxxxx", // 这里填自己服务器微信的鉴权参数注入接口
      type: "POST",
      contentType: "application/json;charset=utf-8",
      data: null,
      dataType: "text",
      success: function (backdata) {
          var jdata = $.parseJSON(backdata);
          wx.config({
              debug: false,
              appId: jdata.appId,
              timestamp: jdata.timestamp,
              nonceStr: jdata.nonceStr,
              signature: jdata.signature,
              jsApiList: ['scanQRCode']
          });

          wx.ready(function () {
              wx.scanQRCode({
                  needResult: 1,
                  desc: 'scanQRCode desc',
                  success: function (res) {
                      var qrdata = $.parseJSON(res.resultStr);
                      window.open("https://aa.aaa.com/api?cid=" + // 这里输入自己服务器的GET接口（用于跳转获得结果）
                          qrdata.course_id + "&ts=" + qrdata.sgin_id + "&r=" + Math.random());
                  },
                  cancel: function () {
                      history.back();
                  }
              });
          });
      }
  });

</script>
</body>
</html>


        """
        return html

    def wxconfig_post(self):
        try:
            ip = flask.request.headers['X-Real-Ip']
        except KeyError:
            ip = flask.request.remote_addr
        logging.debug("来自" + str(ip) + "的客户端开始使用微信扫一扫接口")
        if flask.request.referrer != self.WXClient.get_sig_url():
            logging.warning("Referer错误，拒绝访问")
            return "拒绝访问"
        c = self.WXClient.get_jswxconfig()
        return flask.json.dumps(c)

    def sign(self):
        self.full_table = ""
        html = """
                        <!DOCTYPE html>
                        <html>
                	    <head>
                		<meta charset="utf-8" />
                		<title>Sign Information</title>
                		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
                	    </head>

                	    <body>
                		<h2>
                			<small>感谢你帮我们签到</small>
                		</h2>
                		<br>
                		状态信息如下（请留意是否出现签到成功）：
                		<br>
                		<br>
                		%s
                        <br>
                		<br>
                		<strong>
                			Ice Cream 2019
                		</strong>
                	    </body>
                        </html>
                        """
        try:
            ip = flask.request.headers['X-Real-Ip']
        except KeyError:
            ip = flask.request.remote_addr

        logging.debug("来自" + str(ip) + "的客户端开始使用签到接口")
        if flask.request.referrer != self.WXClient.get_sig_url():
            logging.warning("Referer错误，拒绝访问")
            return "拒绝访问"
        cid = ''.join(list(filter(str.isdigit, str(flask.request.args.get('cid')))))
        ts = ''.join(list(filter(str.isdigit, str(flask.request.args.get('ts')))))
        logging.debug("来自" + str(ip) + "的客户端传来了这些信息：cid" + cid + ",ts:" + ts)

        if cid == "" or ts == "":
            return "拒绝访问"

        for user in users:
            t = threading.Thread(target=self.thread_sign, args=(user, cid, ts))
            t.daemon = True
            t.start()
        threading.Event.wait()

        table = self.__md_conv(self.full_table)

        return html % table

    def thread_sign(self, user, cid, ts):
        self.Lock.acquire()
        table_md = "| Key | Value |\n| ------ | ------ |\n"
        msg = self.post_sign(user, cid, ts)
        table_md = table_md + "| %s | %s |\n" % ("Name", user['name'])
        resp_dict = json.loads(msg)
        keys = list(resp_dict.keys())
        values = list(resp_dict.values())
        for i in range(len(keys)):
            key = str(keys[i])
            value = str(values[i])
            table_md = table_md + "| %s | %s |\n" % (key, value)
        self.full_table = self.full_table + table_md + "\n\n---\n\n"
        self.Lock.release()

    def __md_conv(self, src: str):
        html = (markdown.markdown(src, extensions=[
            'fenced_code',
            'toc',
            'tables',
            'sane_lists'
        ]))
        return html

    def post_sign(self, user, cid, ts):
        """
        用户签到，目前只支持同性别同学校，其他的懒得写了
        :param user: 用户dict
        :param cid: course id qrcode
        :param ts: timestamp qrcode
        :return: 错误信息或者服务端响应
        """
        data = "school_code=4144013675&student_id=" + user['id'] + "&sex=%E7%94%B7&course_id=" + \
               cid + "&sgin_id=" + ts

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "close",
            "X-Requested-With": "com.tencent.mm",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "hd.gzzmedu.com:9080",
            "Referer": user['referer'],
            "User-Agent": "自己抓", # 自己抓
            "Origin": "http://hd.gzzmedu.com:9080",
            "Cookie": user['cookie']
        }

        session = requests.Session()
        url = "http://hd.gzzmedu.com:9080/icsServer/schoolSgin!doNotNeedSecurity_startSgin.do"
        try:
            response = session.post(headers=headers, url=url, timeout=5,
                                    data=data, allow_redirects=False)
        except (requests.exceptions.Timeout, requests.exceptions.BaseHTTPError):
            msg = '{"err": "未知异常，可能是超时或者服务器挂了把，重试一下吧"}'
            logging.error("客户端签到时出了故障，可能是签到服务器挂了")
            session.close()
            return msg

        if int(response.status_code) >= 400:
            code = str(response.status_code)
            logging.error("客户端访问时返回的状态码(" + str(response.status_code) + ")不对")
            msg = '{"err": "状态码错误"}'
            session.close()
            return msg

        msg = str(response.text)
        logging.debug("客户端完成了签到，服务端返回的数据为" + msg)
        session.close()
        return msg


if __name__ == '__main__':
    wx = WeChatJSAPI()
    f = FlaskApp(wx)
