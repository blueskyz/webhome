#!/usr/bin/env python
# coding: utf-8

import os
import logging
import copy
import json

from tornado import httpserver, ioloop, web
from tornado.options import define, options

from clientPlay import clientPlay

define('port', default=8888, help='Run server on a specific port.', type=int)

# global define
g_urldict = []
g_urldict.append({'url': '/tools', 'active': None, 'name': '工具' })
g_urldict.append({'url': '/play/childmusic', 'active': None, 'name': '儿童歌曲', 'path': '/data/resource/music/', 'list': './data/01.json'})
g_urldict.append({'url': '/play/childstory', 'active': None, 'name': '儿童故事', 'path': '/data/resource/music/', 'list': './data/02.json'})
g_urldict.append({'url': '/play/word1', 'active': None, 'name': '新东方单词1', 'path': '/data/resource/xdf/01mp3/', 'list': './data/xdf01.json'})
g_urldict.append({'url': '/play/word2', 'active': None, 'name': '新东方单词2', 'path': '/data/resource/xdf/02mp3/', 'list': './data/xdf02.json'})
g_urldict.append({'url': '/play/word3', 'active': None, 'name': '新东方单词3', 'path': '/data/resource/xdf/03mp3/', 'list': './data/xdf03.json'})
g_urldict.append({'url': '/play/word4', 'active': None, 'name': '新东方单词4', 'path': '/data/resource/xdf/04mp3/', 'list': './data/xdf04.json'})

class mainHandler(web.RequestHandler):
	def get(self, data):
		urldict = copy.deepcopy(g_urldict)
		select = None
		for info in urldict:
			if info['url'].find(data) != -1:
				info['active'] = True
				select = info
				break
		#musicList = json.load(file(info['list'])) if os.path.exists(info['list']) else {}
		# query current play list and status, to show
		self.render('template/index.html', name=select['name'], urldict=urldict)

	def post(self, data):
		'''play music'''
		#play()
		pass

class playHandler(web.RequestHandler):
	def get(self, data):
		urldict = copy.deepcopy(g_urldict)
		for info in urldict:
			if info['url'].find(data) != -1:
				info['active'] = True
				break
		musicList = json.load(file(info['list'])) if os.path.exists(info['list']) else {}
		#urldict = [item for item in urldict if item['url'].find('play') != -1]
		# query current play list and status, to show
		cmdData = {'cmd': 'queryplaylist'}
		cli = clientPlay('192.168.2.18', 4001)
		result = cli.sendLineCmd(json.dumps(cmdData))
		result = json.loads(result)
		if result['ret'] != 0 or result['tag'] != info['url']:
			for item in musicList:
				item['checked'] = ''
		else:
			playlist = result['playlist'] if result.has_key('playlist') else []
			for item in musicList:
				if item['path'] in playlist:
					item['checked'] = 'checked'
				else:
					item['checked'] = ''
		self.render('template/play.html', info=info, urldict=urldict, musicList=musicList)

	def post(self, data):
		'''play music'''
		#urldict = copy.deepcopy(g_urldict)
		cli = clientPlay('192.168.2.18', 4001)
		content = json.loads(self.request.body)
		if content['cmd'] == 'play':
			for info in g_urldict:
				if info['url'] == content['tag']:
					break
			content['playlist'] = [{'_id': item, '_file': info['path'] + item} for item in content['playlist']]
			#print json.dumps(content)
			result = cli.sendLineCmd(json.dumps(content))
			self.write(result)
		else:
			result = cli.sendLineCmd(self.request.body)
			self.write(result)

	def __playMusic(self, data):
		pass

	def __queryStatus(self, data):
		pass

	def __setPlaySound(self, data):
		pass


def run():
	local_static_path = os.path.join(os.path.dirname(__file__), 'static')
	application = web.Application([
		(r'/play/(.*)', playHandler),
		(r'/rest/play/?(.*)', playHandler),
		(r'/(.*)', mainHandler),
		],
		static_path=local_static_path, debug=False)
	http_server = httpserver.HTTPServer(application)
	http_server.bind(options.port)
	http_server.start(2)
	ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	run()

