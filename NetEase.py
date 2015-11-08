# coding=utf-8

from Crypto.Cipher import AES
import base64
import StringIO
import os
import urllib2
import urllib
import yaml
import cookielib
import Constants
import gzip
import re
import logging
import Utility

try:
    import json
except ImportError:
    import simplejson as json

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("NetEase")


class NetEase(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(NetEase, cls)
            cls._instance = orig.__new__(cls, *args)
        return cls._instance

    def __init__(self):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        self.encode = self.NetEaseEncode()
        self.csrf_token = ""

    def __api_request(self, path, data):
        req = urllib2.Request(path + '?csrf_token=' + self.csrf_token)

        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 '
                                     'Chrome/41.0.2272.76 Safari/537.36')
        req.add_header('Referer', 'http://music.163.com/search/')
        req.add_header('Host', 'music.163.com')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Connection', 'keep-alive')
        req.add_header('Accept-Encoding', 'gzip,deflate,sdch')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4')
        req.add_header('Accept', '*/*')

        resp = urllib2.urlopen(req, self.encode.get_data(data))

        # update cookie
        if 'set-cookie' in resp.info().keys():
            str_cookie = resp.info()['set-cookie']
            if str_cookie:
                pattern = re.compile(r'__csrf=(\w+);')
                match = pattern.search(str_cookie)
                if match:
                    token = match.group()[7:-1]
                    if token != self.csrf_token:
                        self.csrf_token = token

        # unpack gzip and return
        try:
            ret_json = gzip.GzipFile(fileobj=StringIO.StringIO(resp.read())).read()
            ret = json.loads(ret_json)
        except IOError, Argument:
            logger.warn("IOError: " + str(Argument))
            logger.warn("resp: " + resp.read())
            return None
        except ValueError, Argument:
            logger.warn("ValueError: " + str(Argument))
            logger.warn("resp: " + resp.read())
            return None
        if ret['code'] != 200:
            Utility.toast("return code is %s" % ret['code'])
            logger.debug(ret_json)
        return ret

    def login(self, username, password, remember=True):
        data = {
            'username': username,
            'password': password,
            'rememberLogin': "true" if remember else "false",
            'csrf_token': self.csrf_token
        }
        return self.__api_request(Constants.login_path, data)

    def user_playlist(self, uid):
        data = {
            'csrf_token': self.csrf_token,
            'limit': "1001",
            'offset': "0",
            'uid': uid
        }
        return self.__api_request(Constants.playlist, data)

    def playlist_detail(self, list_id):
        data = {
            'csrf_token': self.csrf_token,
            'limit': "1000",
            'offset': "0",
            'total': "true",
            'id': list_id
        }
        return self.__api_request(Constants.playlist_detail, data)

    # 内部类,用来加密请求参数
    class NetEaseEncode:
        @staticmethod
        def __padding(string):
            zero_count = 16 - len(string) % 16
            string += "\0" * zero_count
            return string

        def __encrypt_aes(self, key, string):
            pad = 16 - len(string) % 16
            string += pad * chr(pad)
            mode = AES.MODE_CBC
            encrypter = AES.new(key, mode, self.__iv)
            return base64.b64encode(encrypter.encrypt(string))

        @staticmethod
        def __rsa_encrypt(text, pub_key, modulus):
            text = text[::-1]
            rs = int(text.encode('hex'), 16) ** int(pub_key, 16) % int(modulus, 16)
            return hex(long(rs))[2:-1].zfill(256)

        @staticmethod
        def __create_secret_key(size):
            return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

        def get_data(self, src_str):
            text = self.__encrypt_aes(self.key, self.__encrypt_aes(self.__nonce, json.dumps(src_str)))
            enc_sec = self.__rsa_encrypt(self.key, self.__pub_key, self.__modulus)
            return urllib.urlencode({
                'params': text,
                'encSecKey': enc_sec
            })

        def __init__(self):
            config = yaml.load(open('net_ease.conf'))
            self.__nonce = config['nonce']
            self.__pub_key = config['pub_key']
            self.__modulus = config['modulus']
            self.__iv = config['iv']
            self.key = self.__create_secret_key(16)


def get_instance():
    return NetEase()


if __name__ == "__main__":
    pass
    # login_ret_data = net_ease.login("59603803@163.com", Utility.md5("1632bepro"))
    # playlist = net_ease.user_playlist(login_ret_data['account']['id'])
    # songs = net_ease.playlist_detail(playlist['playlist']['0']['id'])
    # songs = net_ease.playlist_detail(42802075)  #
    # for song in songs['result']['tracks']:
    #     print song['name']
