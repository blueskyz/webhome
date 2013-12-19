#!/usr/bin/python

import os
import time
from subprocess import Popen as popen


def play_sound( filename ):
	#p = popen(['./pifm', 'data/waipopenghuwan.wav', '103.3', '44100'])
	p = popen(['./pifm', 'data/01.wav', '103.3', '44100'])
	ret = None
	count = 7
	while count and ret is None:
		time.sleep(3)
		ret = p.poll()
		print ret
		count -= 1
	if count == 0:
		os.kill(p.pid, 15)
	p.wait()
	return

if __name__ == '__main__':
	play_sound('')
