#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import random
from subprocess import Popen as popen

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task
from twisted.application import service

LineReceiver.MAX_LENGTH = 8*1024*1024

_stop_ = 0
_play_ = 1
class player():
	def __init__(self):
		self._playList = []
		self._process = None
		self._random = False
		self._pos = -1
		self._state = _play_

	def addPlayList(self, playList, isRandom):
		self._playList = playList
		if random:
			self._random = isRandom
			random.shuffle(self._playList)
		if len(self._playList) > 0:
			self._pos = 0
			self._state = _play_

	def play(self):
		if self._state == _stop_:
			return
		# running
		if self._process != None:
			if self._process.poll() == None:
				return
			else:
				self._process = None

		print 'test ...'
		if self._process == None and len(self._playList) > 0:
			if len(self._playList) <= self._pos:
				self._pos = 0
				if self._random:
					random.shuffle(self._playList)
			music = self._playList[self._pos]
			print self._pos, music['_id'], music['_file']
			#self._process = popen(['../pifm', music['_file'], '102.3', '44100'])
			self._process = popen(['mpg321', '-q', '-g', '20', music['_file']])
			self._pos += 1

	def stopPlay(self):
		if self._process is not None:
			self._process.poll() == None and os.kill(self._process.pid, 15)
			self._process.wait()
			self._process = None
		self._state = _stop_

	def playNext(self):
		self.stopPlay()
		self._state = _play_

	def getPlayId(self):
		return None if self._process == None or self._pos == -1 else self._playList[self._pos-1]['_id']

stopTimer = 0
def schedule(play):
	# shutdown system
	if stopTimer != 0 and stopTimer <= time.time():
		log.msg('schedule:shutdown, stopTimer:%s, curTime:%s' 
				% (stopTimer, time.time()))

	# control play
	play.play()

play = player()
task = task.LoopingCall(schedule, play)
task.start(3.0)

class playerCtl(LineReceiver):
	def __init__(self):
		self._shutdown = None

	def connectionMade(self):
		out = {}
		out['ret'] = 0
		out['type'] = 'conn'
		out['msg'] = 'connection succ.'
		out['shutdown'] = self._shutdown
		self.sendLine(json.dumps(out))

	def lineReceived(self, line):
		try:
			print 'line recv: ', len(line)
			log.msg(line)
			log.msg(str(time.time()))
			self.parseCmd(json.loads(line))
		except Exception, err:
			out = {'ret': -1, 'msg': err.message + line}
			self.sendLine(json.dumps(out))

	def parseCmd(self, data):
		cmd = data['cmd'].lower()
		print cmd
		if cmd == 'stop':
			play.stopPlay()
			self.transport.loseConnection()
			reactor.stop()
		elif cmd == 'play':
			print 'play cmd'
			self.addPlayList(data)
			# set shutdown time
			global stopTimer
			stopTimer = (time.time() + int(data['stoptimer'])) if data.has_key('stoptimer') else 0
			out = {'ret': 0}
			self.sendLine(json.dumps(out))
			return
		elif cmd == 'playnext':
			play.playNext()
			out = {'msg': 'playnext'}
		elif cmd == 'stopplay':
			play.stopPlay()
			out = {'msg': 'stopplay'}
		elif cmd == 'queryplayid':
			out = {'ret': 0, 'msg': play.getPlayId()}
			print 'ret queryplayid .........', json.dumps(out)
		else:
			out = {'ret': -1, 'msg': 'invalid command, ' + str(cmd)}

		self.sendLine(json.dumps(out))

	def addPlayList(self, data):
		playList = data['playlist'] if data.has_key('playlist') else []
		if len(playList) == 0:
			playList = []
		# random
		isRandom = False if data.has_key('sort') else True
		play.stopPlay()
		play.addPlayList(playList, isRandom)
		# test
		#play.addPlayList([{'_id':0, '_file':'../data/01.wav'},
		#	{'_id':1, '_file':'../data/waipopenghuwan.wav'},
		#	{'_id':2, '_file':'../data/qiyue.wav'}], True)


class playerFactory(Factory):
	def buildProtocol(self, addr):
		return playerCtl()

class playerServ(service.Service):
	def __init__(self):
		pass

	def startService(self):
		self._serv = reactor.listenTCP(4001, playerFactory())

	def stopService(self):
		return self._serv.stopListening()

application = service.Application('Player serv.')
playerServ().setServiceParent(application)

if __name__ == '__main__':
	log.startLogging(open('./run.log', 'w'))
	reactor.listenTCP(4001, playerFactory())
	reactor.run()

