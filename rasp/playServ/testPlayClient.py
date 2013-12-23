#!/usr/bin/env python
# coding: utf-8

import time
import json
import socket

class clientPlay():
	def __init__(self, ip, port):
		self._ip = ip
		self._port = port

	def sendLineCmd(self, data):
		try:
			s = socket.create_connection((self._ip, self._port),
					timeout=5)
			s.settimeout(5)
			print 'send data: ', data
			s.sendall(data + '\r\n')
			result = s.recv(1024)
			count = 0
			pos = 0
			while True:
				#print len(result), result
				newpos = result.find('\r\n', pos)
				if -1 != newpos:
					count += 1
					if count == 2:
						ret = result[pos:newpos]
						break
					pos = newpos + 2
				else:
					result += s.recv(1024)
			print 'result: ', ret, pos, len(result), result
			s.close()
			return ret
		except Exception, err:
			print err
			result = {'ret': -1}
			result['msg'] = err.message
			return json.dumps(result)

def main():
	cli = clientPlay('192.168.2.18', 4001)
	musics = json.load(file('./02.json'))
	for music in musics:
		music['_id'] = music['path']
		music['_file'] = '/data/resource/music/' + music['path']
	print 'len: ', len(musics)
	cmdPlay = {}
	cmdPlay['cmd'] = 'play'
	cmdPlay['playlist'] = musics
	result = cli.sendLineCmd(json.dumps(cmdPlay))
	print 'receive: ', time.time(), result

	count = 0
	while True:
		time.sleep(8)
		result = cli.sendLineCmd('{"cmd":"playnext", "time":%d}' % (time.time()))
		print result
		time.sleep(20)
		result = cli.sendLineCmd('{"cmd":"queryplayid", "time":%d}' % (time.time()))
		print 'queryplayid', result
		time.sleep(10)
		count += 1

if __name__ == '__main__':
	main()

