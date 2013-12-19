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


class player():
	def __init__(self):
		self._playList = []
		self._process = None
		self._random = False
		self._pos = 0

	def addPlayList(self, playList, isRandom):
		self._playList = playList
		if random:
			self._random = isRandom
			random.shuffle(self._playList)
		if len(self._playList) > 0:
			self._pos = 0

	def play(self):
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
			print self._playList[self._pos], self._pos, self._playList
			self._process = popen(['../pifm', self._playList[self._pos], '103.3', '44100'])
			self._pos += 1

	def stopPlay(self):
		if self._process is not None:
			self._process.poll() == None and os.kill(self._process.pid, 15)
			self._process.wait()
			self._process = None

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
		self.sendLine('connection succ.')
		out = {}
		out['ret'] = 0
		out['shutdown'] = self._shutdown
		self.sendLine(json.dumps(out))

	def lineReceived(self, line):
		try:
			self.parseCmd(json.loads(line))
		except Exception, err:
			out = {'ret': -1, 'msg': err.message + line}
			self.sendLine(json.dumps(out))

	def parseCmd(self, data):
		cmd = data['cmd'].lower()
		if cmd == 'stop':
			play.stopPlay()
			self.transport.loseConnection()
			reactor.stop()
		elif cmd == 'play':
			self.addPlayList(data)
		else:
			out = {'ret': -1, 'msg': 'invalid command, ' + str(cmd)}
			self.sendLine(json.dumps(out))
			return

		# set shutdown time
		global stopTimer
		stopTimer = (time.time() + int(data['stoptimer'])) if data.has_key('stoptimer') else 0
		out = {'ret': 0}
		self.sendLine(json.dumps(out))

	def addPlayList(self, data):
		playList = data['playlist'] if data.has_key('playlist') else []
		if len(playList) == 0:
			playList = []
		# random
		isRandom = True if data.has_key('playtype') else False
		play.stopPlay()
		#play.addPlayList(playList, isRandom)
		# test
		play.addPlayList(['../data/01.wav', '../data/waipopenghuwan.wav'], True)

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

