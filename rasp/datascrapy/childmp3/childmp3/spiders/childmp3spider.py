#!/usr/bin/env python
# coding: utf-8

import math

from scrapy.spider import Request
from scrapy.spider import BaseSpider
from scrapy.spider import log
from scrapy.selector import Selector as selector

from childmp3.items import Childmp3Item as childmp3Item

class childmp3Spider(BaseSpider):
    name = 'childmp3'
    allowed_domains = ['9ku.com']
    start_urls = ['http://www.9ku.com/erge/ertonggequ.htm',
            #'http://www.9ku.com/erge/gushi.htm'
			]
    mp3_url = 'http://mp3.9ku.com/file2/%d/%s.mp3'

    def parse(self, response):
        hxs = selector(response)
        typename = hxs.xpath('//li/a[@class="active"]/text()').extract()
        self.log(typename[0].encode('gbk'))
        urls = hxs.css('.songList ol li a[class="songName"]')
        requestItem = []
        for url in urls:
            href = url.xpath('@href').extract()[0]
            name = url.xpath('text()').extract()[0]
            id = href[href.rfind('/')+1:href.rfind('.')]
            hash = int(math.ceil(float(id)/1000.0))
            mp3Url = self.mp3_url % (hash, id)
            self.log(mp3Url)
            requestItem.append(Request(mp3Url, 
                    callback=self.parseMp3, 
                    meta={'name': name, 'id':id, 'typename': typename}))
        return requestItem

    def parseMp3(self, response):
        self.other = {'id': response.meta['id'],
                'body': response.body}
        item = childmp3Item()
        item['path'] = './mp3/' + response.meta['id'] + '.mp3'
        item['name'] = response.meta['name']
        item['typename'] = response.meta['typename']
        self.log(item['name'].encode('gbk'))
        return item

