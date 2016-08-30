#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, signal, subprocess, socks, socket, time, re, http.client, datetime, json
from urllib import request

HTML_DIR = '/usr/share/nginx/html/'
# HTML_DIR = ''

TEST_URL = 'https://lh3.googleusercontent.com/-ycsvDrTOuqo/Vkuu015PfXI/AAAAAAAAN-o/G8EzTXj65Dg/w3840-h2160/london-city-chromecast-wallpaper-4k.jpg'

CLS_CMD = 'ps aux | grep "\-l 1088" | kill `awk \'NR==1{print $2}\'`'
SS_CMD = 'sslocal -s {server_addr} -p {server_port} -b 127.0.0.1 -l 1088 -k \'{password}\' -m {method} -t 3 --fast-open &> /dev/null'


def get_current_time():
	now = datetime.datetime.now()
	return now.strftime('%Y-%m-%d %H:%M:%S')


def calc_speed(func):
	def wrapper():
		start = time.time()
		size = func()
		end = time.time()
		return int(size / 1024 / (end - start))

	return wrapper


def calc_time(func):
	def wrapper():
		start = time.time()
		func()
		end = time.time()
		return round(end - start, 2)

	return wrapper


class SSLinker:
	def __init__(self, url):
		self.url = url
		self.tmp = url[5:]
		self.__method().__remark().__port().__ip().__auth()

	def __method(self):
		sep = self.tmp.find(':')
		if self.tmp[sep] != ':':
			raise Exception('interpretation error')
		self.method = self.tmp[:sep]
		self.tmp = self.tmp[sep:]
		return self

	def __remark(self):
		sep = self.tmp.rfind('#')
		if self.tmp[sep] != '#':
			raise Exception('interpretation error')
		self.remark = self.tmp[sep:][1:].strip()
		self.tmp = self.tmp[:sep]
		return self

	def __port(self):
		sep = self.tmp.rfind(':')
		if self.tmp[sep] != ':':
			raise Exception('interpretation error')
		self.port = self.tmp[sep:][1:]
		self.tmp = self.tmp[:sep]
		return self

	def __ip(self):
		sep = self.tmp.rfind('@')
		if self.tmp[sep] != '@':
			raise Exception('interpretation error')
		self.addr = self.tmp[sep:][1:]
		self.tmp = self.tmp[:sep]
		return self

	def __auth(self):
		self.auth = self.tmp[1:]


class SSConner(SSLinker):
	def __init__(self, url):
		super(SSConner, self).__init__(url)
		self.resp = None
		self.delay = 9.9
		self.speed = 0

	def conn(self):
		os.system(CLS_CMD)
		self.proc = subprocess.Popen(SS_CMD.format(**{
			'server_addr': self.addr,
			'server_port': self.port,
			'password': self.auth,
			'method': self.method,
		}), shell=True, start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def download(self):

		def create_connection(address, timeout=None, source_address=None):
			sock = socks.socksocket()
			sock.connect(address)
			return sock

		def block():
			@calc_time
			def connect():
				self.resp = request.urlopen(TEST_URL)

			retry = 5
			while retry > 0:
				try:
					time.sleep(0.1)
					self.delay = connect()
				except:
					retry = retry - 1
				else:
					break

		def download_file():
			@calc_speed
			def read():
				try:
					recv = self.resp.read()
					self.resp.close()
					return len(recv)
				except http.client.IncompleteRead as e:
					return int(re.findall('[0-9]+', str(e))[0])
				except Exception as e:
					return 0

			self.speed = read()

		socket.setdefaulttimeout(3)
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1088)
		socket.socket = socks.socksocket
		socket.create_connection = create_connection

		block()
		download_file()

		self.proc.terminate()
		self.proc.wait()

		try:
			os.killpg(self.proc.pid, signal.SIGTERM)
		except OSError as e:
			pass

		self.output()

		return {
			'url': self.url,
			'addr': self.addr,
			'remark': self.remark,
			'delay': self.delay,
			'speed': self.speed
		}

	def output(self):
		def format(str, occupied=1):
			length = len(str.encode('GBK'))
			return str if length >= 16 * occupied else str + ('\t' * (occupied - (length + 1) // 16))

		def toTable():
			f = open(HTML_DIR + "process.txt", 'a+', encoding='UTF-8')
			print(format('[TIME]:%s' % get_current_time(), 2),
				  format('[ADDR]:%s' % self.addr, 2),
				  format('[DELAY]:%ss' % self.delay, 2),
				  format('[SPEED]:%sKB/s' % self.speed, 2),
				  '[REMARK]:%s' % self.remark,
				  file=f)
			f.close()

		toTable()


def main():
	def output_result():
		with open(HTML_DIR + "result.json", 'w+', encoding='UTF-8') as f1, \
				open(HTML_DIR + "result.jsonp", 'w+', encoding='UTF-8') as f2:
			print(json.dumps(result), file=f1)
			print('callback(' + json.dumps(result) + ')', file=f2)

	def read_last_result():
		try:
			f = open(HTML_DIR + "result.json", 'r', encoding='UTF-8')
			ex_result = f.read()
			ex_dict = json.loads(ex_result)
			for it in ex_dict['ssList']:
				last_result[it['addr']] = {
					'last_delay': it['delay'],
					'last_speed': it['speed']
				}
		except:
			pass

	SSList = []
	last_result = {}
	read_last_result()
	resp = request.urlopen("http://blog.heycis.com/manage/ss.txt")
	content = resp.read().decode("utf-8").split('\n')
	for line in content:
		if line:
			try:
				client = SSConner(line)
			except Exception as e:
				continue
			client.conn()
			result = client.download()
			try:
				result['last_delay'] = last_result[result['addr']]['last_delay']
				result['last_speed'] = last_result[result['addr']]['last_speed']
			except:
				result['last_delay'] = 9.9
				result['last_speed'] = 0
			SSList.append(result)

	# SSList.sort(key=lambda o: (-o['speed'], o['delay']))
	output_result()


if __name__ == '__main__':
	main()
