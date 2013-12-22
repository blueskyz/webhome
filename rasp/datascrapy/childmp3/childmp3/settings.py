# Scrapy settings for childmp3 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'childmp3'

SPIDER_MODULES = ['childmp3.spiders']
NEWSPIDER_MODULE = 'childmp3.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'childmp3 (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22 AlexaToolbar/alxg-3.1"

#DOWNLOAD_DELAY = 4
ITEM_PIPELINES = {
        'childmp3.pipelines.Childmp3Pipeline': 300
        }
