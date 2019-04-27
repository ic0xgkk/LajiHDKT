import flask
import logging
import time
import json
import requests

logname = time.strftime("%Y%m%d%H%M%S", time.localtime())
logname = './log/lajihdkt-' + logname + '.log'
logging.basicConfig(filename=logname,
                    level=logging.DEBUG,
                    format='[%(levelname)s:%(asctime)s] %(message)s')
logging.warning("Server started")


class FlaskApp(object):
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.url_route()
        self.start()

    def start(self):
        self.app.run(host="0.0.0.0", port=6666, debug=False, threaded=True)

    def url_route(self):
        self.app.add_url_rule('/api', 'sign', self.sign, methods=['GET'])

    def sign(self):
        msg = ""
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
			<small>感谢你帮我签到</small>
		</h2>
		<br>
		状态信息如下（请留意是否出现签到成功）：
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
        ip = flask.request.remote_addr
        logging.debug("来自" + str(ip) + "的客户端开始使用这个接口")
        qr = str(flask.request.args.get('qrresult'))
        logging.debug("来自" + str(ip) + "的客户端传来了这些信息：" + qr)
        try:
            qrj = json.loads(qr)
        except json.JSONDecodeError:
            logging.error("来自" + str(ip) + "的客户端传来的参数有问题，可能是在搞破坏，传入数据为" + qr)
            msg = "有毛病"
            return html % msg

        data = "school_code=学校id&student_id=学号&sex=自己抓&course_id=" + str(qrj['course_id'])\
                + "&sgin_id=" + str(qrj['sgin_id'])

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "close",
            "X-Requested-With": "com.tencent.mm",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "hd.gzzmedu.com:9080",
            "Referer": "",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; ONEPLUS A5000 Build/PKQ1.180716.001; wv) AppleWebKit"
                          "/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 Mobile Safari/537.36 MMWE"
                          "BID/7933 MicroMessenger/7.0.3.1381(0x27000340) Process/tools NetType/WIFI Language/zh_CN",
            "Origin": "http://hd.gzzmedu.com:9080",
            "Cookie": "JSESSIONID=aaaaaaaaa"
        }

        session = requests.Session()
        url = "http://hd.gzzmedu.com:9080/icsServer/schoolSgin!doNotNeedSecurity_startSgin.do"
        try:
            response = session.post(headers=headers, url=url, timeout=5,
                                    data=data, allow_redirects=False)
        except (requests.exceptions.Timeout, requests.exceptions.BaseHTTPError):
            msg = "未知异常，可能是超时或者服务器挂了把，重试一下吧"
            logging.error("来自" + str(ip) + "的客户端签到时出了故障，可能是签到服务器挂了，传入数据为" + qr)
            session.close()
            return html % msg

        if int(response.status_code) >= 400:
            code = str(response.status_code)
            logging.error("来自" + str(ip) + "的客户端访问时返回的状态码(" + str(response.status_code) + ")不对，传入数据为" + qr)
            msg = "状态码错误：%s" % code
            session.close()
            return html % msg

        msg = str(response.text)
        logging.debug("来自" + str(ip) + "的客户端完成了签到，服务端返回的数据为" + msg)
        session.close()
        return html % msg


if __name__ == '__main__':
    f = FlaskApp()
