import re
import time
import scrapy
import pymongo
from pigat.items import PigatItem_ip


class pigat_ip(scrapy.Spider):
	name = 'pigat_ip'

	def start_requests(self):
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
		ip_headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
		}
		url = self.url  # 待爬取 URL

		client = pymongo.MongoClient('localhost', 27017)  # 连接数据库
		collection = client['pigat']['pigat_subdomain']  # 读取数据
		if list(collection.find({'url': url})) == []:  # 判断数据是否为空
			print(
				'\n\033[1;31;40m[{}] 数据库中未查询到 {} 的子域信息，无法进行 {} 的子域 IP 查询，请先获取 {} 的子域信息\n\033[0m'.format(time.strftime('%Y-%m-%d %H:%M:%S'),
				                                                                    url, url, url))
		else:
			print('\n\033[1;33;40m[{}] 正在被动收集 {} 的子域 IP 信息……\033[0m'.format(time.strftime('%Y-%m-%d %H:%M:%S'), url))
			print('\033[1;33;40m[{}] 提示：如果出现大量无法判断 IP 的情况，请尝试更换自己的IP\033[0m'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
			for i in collection.find({'url': url}):
				subdomain_url = i['subdomain_url']
				# 子域IP查询
				ip_url = "http://tools.bugscaner.com/api/nslookup/"
				yield scrapy.FormRequest(url=ip_url, headers=ip_headers,
				                         meta={'url': url, 'subdomain_url': subdomain_url, 'ip_url': ip_url,
				                               'headers': headers},
				                         formdata={"inputurl": subdomain_url},
				                         callback=self.sub_ip)

	def sub_ip(self, response):
		url = response.meta['url']
		subdomain_url = response.meta['subdomain_url']
		ip_result = list(set((re.findall(r'\d+.\d+.\d+.\d+', response.text))))  # 通过正则获取响应中的IPv4地址，并对结果去重
		if len(ip_result) == 1:
			sub_ip = ip_result[0]
			print(
				'\033[1;32;40m[{}] {}\t{}\t\t{}\033[0m'.format(time.strftime('%Y-%m-%d %H:%M:%S'), url, subdomain_url,
				                                             sub_ip))
			item = PigatItem_ip(
				url=url,
				subdomain_url=subdomain_url,
				sub_ip=sub_ip
			)
			yield item
		else:
			print('\033[1;32;40m[{}] {}\t{}\t\t{}\033[0m'.format(time.strftime('%Y-%m-%d %H:%M:%S'), url,
			                                                   subdomain_url, '无法判断 IP'))
