# -*- coding: utf-8 -*-
"""
:author: Punk Lee
:datetime: 2020/4/21 22:02
:url: https://punk_lee.gitee.io/
:copyright: ©2020 Punk Lee <punklee333@gmail.com>
"""
import requests, os, json
from lxml.html import etree
from retrying import retry
from datetime import datetime
from http.cookiejar import MozillaCookieJar


def secure_retry(f):
    from functools import wraps
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(e.args)
            return False

    return inner


class Freenom:
    def __init__(self, username, password, **kwargs):
        """
        init params
        :param username: your username
        :type username: str
        :param password: your password
        :type password: str
        """
        # path setup
        self._path = os.getcwd()
        self._cookies_path = os.path.join(os.getcwd(), 'cookies_data')
        self._data_path = os.path.join(os.getcwd(), 'freenom_data')
        # user setup
        self.username = username
        self.password = password
        # request setup
        self.headers = {
            'Host': 'my.freenom.com',
            'Referer': 'https://my.freenom.com/clientarea.php',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        }
        self.session = requests.session()
        self.session.headers = self.headers
        self.token = ''
        # cookies setup
        cookies = MozillaCookieJar(filename=self._cookies_path)
        if os.path.isfile(self._cookies_path):
            cookies.load(self._cookies_path, ignore_discard=True, ignore_expires=True)
        self.session.cookies = cookies
        # option setup --dev
        self.timeout = kwargs.get('timeout', 22)
        self.saveHtml = kwargs.get('saveHtml', False)

        # is loggedIn?
        if not self._loggedIn():
            self.doLogin()

    @secure_retry
    @retry(stop_max_attempt_number=3, wait_random_min=2000, wait_random_max=6000)
    def _request(self, req, url, **kwargs):
        print('*', end='')
        kwargs = {
            'data': kwargs.get('data', {}),
            'timeout': kwargs.get('timeout', self.timeout),
            'headers': kwargs.get('headers', self.headers)
        }
        # send request
        return req(url, **kwargs)

    def _saveHtml(self, html_text, filename='res'):
        if self.saveHtml:
            with open(f'{self._path}/{filename}.html', 'w', encoding='utf-8') as f:
                time = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f.write(f'<!--{time}-->')
                f.write(html_text)

    def _parse(self, html_text, xpath):
        try:
            self._saveHtml(html_text)
            element = etree.HTML(html_text)
            return element.xpath(xpath)
        except Exception as e:
            print('parse fail:', end=' ')
            return []

    def _getData(self):
        """get local domain_data"""
        data = {}
        try:
            if not os.path.isfile(self._data_path):
                self._RequireData()
            with open(self._data_path, encoding='utf-8') as f:
                data = json.loads(f.read())
        except Exception as e:
            print(e)
            return data

        return data

    def _RequireData(self):
        """Cache all domain and domain_id to local"""
        print('cacheData:', end=' ')

        domains_data = {}
        url = "https://my.freenom.com/clientarea.php?action=domains"
        res = self._request(self.session.get, url)
        # parse html text
        domains = self._parse(res.text, "//td[@class='second']//text()")
        href = self._parse(res.text, "//td[@class='seventh']//a/@href")
        if domains and href:
            domains = [i.strip() for i in domains[:] if i.strip()]
            id = [i.split('=')[-1] for i in href[:]]
            domains_data = dict(zip(domains, id))
        # Save as local file
        with open(self._data_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(domains_data))

        return domains_data

    def _getRecordList(self, domain, domainid):
        data = []

        url = 'https://my.freenom.com/clientarea.php?managedns=%s&domainid=%s' % (domain, domainid)
        res = self._request(self.session.get, url)
        recordslist = self._parse(res.content.decode(), '//*[@id="recordslistform"]/table/tbody/tr')
        if recordslist:
            for record in recordslist:
                tmp_list = []
                name = record.xpath('./td[@class="name_column"]//input[@type="text"]/@value')[0]
                type = record.xpath('./td[@class="type_column"]//text()')[0]
                ttl = record.xpath('./td[@class="ttl_column"]//input[@type="text"]/@value')[0]
                target = record.xpath('./td[@class="value_column"]//input[@type="text"]/@value')[0]
                tmp_list.append(name)
                tmp_list.append(type)
                tmp_list.append(ttl)
                tmp_list.append(target)
                data.append(tmp_list)

        return data

    def _loggedIn(self):
        print('LoggedIn:', end=' ')
        url = 'https://my.freenom.com/clientarea.php'

        res = self._request(self.session.get, url)
        loggedIn = self._parse(res.content.decode(), '//body/@class')[0]
        ret = 'loggedIn' in loggedIn
        print(ret)
        if not ret:
            print('GetToken:', end=' ')
            self.token = self._parse(res.content.decode(), '//input[@name="token"]/@value')[0]
            print(self.token)

        return ret

    def doLogin(self, username=None, password=None):
        print('doLogin:', end=' ')

        url = 'https://my.freenom.com/dologin.php'
        form_data = {
            'token': self.token if self.token else '',
            'username': username if username else self.username,
            'password': password if password else self.password
        }

        # send request and save cookies as local
        res = self._request(self.session.post, url, data=form_data)
        if res.url.find('incorrect=true') != -1:
            print(self._parse(res.content.decode(), '//div[contains(@class,"error-message")]/p/text()')[0])
            exit()
        else:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            print('Login successfully.')

    def _isAddRecord(self, records, name):
        # No records
        if not records:
            return True
        # no name in records
        for record in records:
            if name == record[0]:
                return False

        return True

    def _showDnsResult(self, html_text, xpath_list):
        # show dns result
        for xpath in xpath_list:
            dns_res = self._parse(html_text, xpath)
            if dns_res:
                print(dns_res[0])
                break

    def setRecord(self, domain, name, type, target, ttl='3600'):
        """
        add or modify record
        :param domain: <xxx.ga>
        :param name: <www>
        :param type: <CNAME>
        :param target: <0.0.0.0>
        :param kwargs: ttl|...
        :type domain: str
        :type name: str
        :type type: str
        :type target: str
        :type ttl: str
        """
        data = self._getData()
        print('setRecord:', end=' ')

        # init params
        url = 'https://my.freenom.com/clientarea.php?managedns=%s&domainid=%s'
        name = name.upper()
        type = type.upper()
        ttl = str(ttl)
        target = str(target)
        # add or modify?
        records = self._getRecordList(domain, data[domain])
        if self._isAddRecord(records, name):
            # add
            form_data = {
                'token': '',
                'dnsaction': 'add',
                'addrecord[0][name]': name,
                'addrecord[0][type]': type,
                'addrecord[0][ttl]': ttl,
                'addrecord[0][value]': target,
            }
        else:
            # modify
            form_data = {
                'token': '',
                'dnsaction': 'modify',
            }
            for i in range(len(records)):
                if type == records[i][1]:
                    if name == records[i][0]:
                        records[i][3] = target
                form_data[f'records[{i}][name]'] = records[i][0]
                form_data[f'records[{i}][type]'] = records[i][1]
                form_data[f'records[{i}][ttl]'] = records[i][2]
                form_data[f'records[{i}][value]'] = records[i][3]

        # send request
        res = self._request(self.session.post, url % (domain, data[domain]), data=form_data)
        # show dns result
        if res:
            self._showDnsResult(res.content.decode(),
                                ['//div[@class="recordslist"]/ul/li/text()', '//section[@class="domainContent"]//p'])

    def delRecord(self, domain, name, type='', target='', ttl='3600'):
        """
        del record
        :param domain: <xxx.ga>
        :param name: <www>
        :param type: <CNAME>
        :param target: <0.0.0.0>
        :param kwargs: ttl|...
        :type domain: str
        :type name: str
        :type type: str
        :type target: str
        :type ttl: str
        """
        data = self._getData()
        print('delRecord:', end=' ')

        # init params
        url = 'https://my.freenom.com/clientarea.php?' \
              'managedns={}&' \
              'records={}&' \
              'dnsaction=delete&' \
              'name={}&' \
              'value={}&' \
              'ttl={}&' \
              'domainid={}'
        name = name.upper()
        type = type.upper()
        ttl = str(ttl)
        target = str(target)
        domainid = data.get(domain, '')
        records = self._getRecordList(domain, domainid)
        if records:
            for record in records:
                if name == record[0]:
                    type = record[1]
                    ttl = record[2]
                    target = record[3]

            # send request
            res = self._request(self.session.get, url.format(domain, type, name, target, ttl, domainid))
            # show dns result
            if res:
                self._showDnsResult(res.content.decode(),
                                    ['//div[@class="recordslist"]/ul/li/text()',
                                     '//section[@class="domainContent"]//p'])
        else:
            print('no records to delete')

    def showRecords(self, domain):
        data = self._getData()
        records = self._getRecordList(domain, data.get(domain, ''))
        print()
        print(f'{"-" * 19}showRecords{"-" * 19}')
        if records:
            for record in records:
                print(record)
        else:
            print(f'{"-" * 14}No records to display{"-" * 14}')

    def getPublicIP(self, url='https://api.ipify.org'):
        print(f'PublicIP:', end=' ')
        res = self._request(requests.get, url, headers={})
        pub_ip = res.content.decode()
        print(pub_ip)
        return pub_ip
