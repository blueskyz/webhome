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
		self._playTag = None
		self._playList = []
		self._process = None
		self._random = False
		self._pos = -1
		self._state = _play_
		self._sound = 50
		self.loadLastCfg()

	def addPlayList(self, playTag, playList, isRandom, sound = 50):
		self._playTag = playTag
		self._playList = playList
		self._random = isRandom
		self._sound = int(sound)
		if self._random:
			random.shuffle(self._playList)
		if len(self._playList) > 0:
			self._pos = 0
			self._state = _play_
		self.saveCurrentCfg()

	def play(self):
		if self._state == _stop_:
			return
		# running
		if self._process != None:
			if self._process.poll() == None:
				return
			else:
				self._process = None

		if self._process == None and len(self._playList) > 0:
			if len(self._playList) <= self._pos:
				self._pos = 0
				if self._random:
					random.shuffle(self._playList)
			music = self._playList[self._pos]
			print self._pos, music['_id'], music['_file']
			#self._process = popen(['../pifm', music['_file'], '102.3', '44100'])
			os.system('amixer cset numid=3 1')
			self._process = popen(['mpg321', '-q', '-g', str(self._sound), music['_file']])
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

	def setPlaySound(self, sound):
		self._sound = int(sound)
		self.saveCurrentCfg()

	def getPlaySound(self):
		return self._sound

	def getSort(self):
		return 0 if self._random else 1

	def getPlaylist(self):
		return [item['_id'] for item in self._playList]

	def getPlayTag(self):
		return self._playTag

	def getPlayStatus(self):
		return self._state

	def saveCurrentCfg(self):
		try:
			with open('/tmp/servPlay.json', 'w+') as f:
				serialize = {}
				serialize['playTag'] = self._playTag
				serialize['playList'] = self._playList
				serialize['sound'] = self._sound
				serialize['random'] = self._random
				json.dump(serialize, f)
		except Exception, err:
			print err.message

	def loadLastCfg(self):
		try:
			with open('/tmp/servPlay.json', 'r+') as f:
				serialize = json.load(f)
				self._playTag = serialize['playTag']
				self._playList = serialize['playList']
				self._sound = serialize['sound']
				self._random = serialize['random']
				self._process = None
				self._pos = -1
				self._state = _play_
		except Exception, err:
			print err.message

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
		if cmd == 'shutdown':
			play.stopPlay()
			self.transport.loseConnection()
			reactor.stop()
		elif cmd == 'play':
			print 'play cmd'
			self.addPlayList(data)
			# set shutdown time
			global stopTimer
			stopTimer = (time.time() + int(data['stoptimer']) * 60) if data.has_key('stoptimer') else 0
			out = {'ret': 0}
			self.sendLine(json.dumps(out))
			return
		elif cmd == 'sound':
			play.setPlaySound(data['sound'] if data.has_key('sound') else 50)
			out = {'msg': 'sound'}
		elif cmd == 'playnext':
			play.playNext()
			out = {'msg': 'playnext'}
		elif cmd == 'stopplay':
			play.stopPlay()
			out = {'msg': 'stopplay'}
		elif cmd == 'queryplayid':
			out = {'ret': 0, 
					'msg': play.getPlayId(), 
					'tag': play.getPlayTag(),
					'sound': play.getPlaySound(), 
					'sort': play.getSort(),
					'state': play.getPlayStatus(),
					'lefthalttime': (stopTimer-time.time())/60}
			print 'ret queryplayid .........', json.dumps(out)
		elif cmd == 'queryplaylist':
			out = {'ret': 0, 
					'msg': play.getPlayId(), 
					'tag': play.getPlayTag(),
					'sound': play.getPlaySound(), 
					'sort': play.getSort(),
					'state': play.getPlayStatus(),
					'lefthalttime': (stopTimer-time.time())/60,
					'playlist': play.getPlaylist()}
		else:
			out = {'ret': -1, 'msg': 'invalid command, ' + str(cmd)}

		self.sendLine(json.dumps(out))

	def addPlayList(self, data):
		playList = data['playlist'] if data.has_key('playlist') else []
		if len(playList) == 0:
			playList = []
		# play tag
		playTag = data['tag'] if data.has_key('tag') else None
		# random
		isRandom = False if data.has_key('sort') else True
		# sound
		sound = data['sound'] if data.has_key('sound') else 50
		print 'sort: ', isRandom
		print 'sound: ', sound
		play.stopPlay()
		play.addPlayList(playTag, playList, isRandom, sound)
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

