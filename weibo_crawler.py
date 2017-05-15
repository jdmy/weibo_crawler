import requests
import base64
import re
import urllib
import urllib.parse
import rsa
import json
import binascii
import weibo_crawl.dao
from bs4 import BeautifulSoup


class Userlogin:
    def crawl_user(self, f_id, session):
        # f_id="5651669201"
        follow_url = "http://weibo.com/u/" + f_id
        resp = session.get(follow_url)
        # 微博的爬虫判断指纹是<div class="WB_text W_f14".*?/div>,但是爬取下来的文本有转义字符所以变成<div class=\\"WB_text W_f14\\".*?/div>

        follow_weibo = re.findall("(<div class=\\\\\"WB_text W_f14\\\\\".*?\/div>)", resp.text)
        follow_weibo_time=re.findall("(<div class=\\\\\"WB_from S_txt2\\\\\".*?\/div>)",resp.text)
        follow_nickname=re.findall("<title>(.*?)\u7684\u5FAE\u535A_\u5FAE\u535A<\/title>",resp.text)

        print(follow_nickname)
        strs=[]
        ntrs=[]
        #对微博时间的处理
        if follow_weibo_time!=[]:
        #爬取初次点进微博主页可以看到的所有微博，即只显示最近的几条微博
            time_strs=["".join(weibo.split("\\")) for weibo in follow_weibo_time]
            time_soups=[BeautifulSoup(str) for str in time_strs]
            trs = [soup.find("div") for soup in time_soups]
            ntrs=[]
            for soup in trs:
                soups=soup.find_all("a")
                # print(soups)
                for s in soups:
                    if s.has_attr("name"):
                        # print(s.text+"name")
                        ntrs.append(s.text)
            # print("********",len(time_soups))
            # print("%%%%%%%%", len(ntrs))
        #对微博的处理
        if follow_weibo!=[]:
        #爬取初次点进微博主页可以看到的所有微博，即只显示最近的几条微博
            strs=["".join(weibo.split("\\")) for weibo in follow_weibo]
        trs=[]
        if strs !=[]:
            #一些文本的处理
            soups=[BeautifulSoup(str) for str in strs]
            trs=[soup.find("div").text for soup in soups]
            trs=[tr.replace(" ","") for tr in trs]
            trs = [tr[1:] for tr in trs]
            # print("#########",len(trs))
            # print(trs[0])
            #
            # print(ntrs[0])
            #
            # print(trs[1])
            # print(ntrs[1])
            #写进文件
            # with open("follow"+follow_nickname[0]+".text",encoding="utf-8", mode="w+") as f:
            #     for tr in trs:
            #         f.write(tr+"\n")

            #数据库操作
            weibo_dao=weibo_crawl.dao.dao()
            weibo_dao.create_if_not_exist()
            for i in range(len(trs)):
                weibo_dao.insert(f_id,trs[i],follow_nickname[0],ntrs[i])
            weibo_dao.search(follow_nickname[0])

        pass

    def userlogin(self, username, password, pagecount):
        session = requests.Session()
        url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625'
        url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
        resp = session.get(url_prelogin)
        json_data = re.findall(r'(?<=\().*(?=\))', resp.text)[0]
        data = json.loads(json_data)
        print(json_data)

        servertime = data['servertime']
        nonce = data['nonce']
        pubkey = data['pubkey']
        print(pubkey)
        rsakv = data['rsakv']

        # calculate su
        print(urllib.parse.quote(username))
        su = base64.b64encode(username.encode(encoding="utf-8"))

        # calculate sp
        rsaPublickey = int(pubkey, 16)
        # print(rsaPublickey)
        key = rsa.PublicKey(rsaPublickey, 65537)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        sp = binascii.b2a_hex(rsa.encrypt(message.encode(encoding="utf-8"), key))
        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsakv': rsakv,
        }
        resp = session.post(url_login, data=postdata)
        with open("test1.html", encoding="utf-8", mode="w") as f:
            f.write(resp.text)

        login_url = re.findall(r'http://weibo.*&retcode=0', resp.text)

        respo = session.get(login_url[0])

        uid = re.findall('"uniqueid":"(\d+)",', respo.text)[0]
        url = "http://weibo.com/" + uid + "/follow"
        respo = session.get(url)
        with open("test2.html", encoding="utf-8", mode="w") as f:
            f.write(respo.text)
        follow_id_li = re.findall("member_li S_bg1.*?uid=(\d*)\D", respo.text)
        for f_id in follow_id_li:
            self.crawl_user(f_id, session)


a = Userlogin()
a.userlogin("usermail", "password", 1)
