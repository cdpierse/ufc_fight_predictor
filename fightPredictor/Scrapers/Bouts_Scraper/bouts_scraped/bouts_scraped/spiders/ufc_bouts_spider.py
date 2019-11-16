import sys

import scrapy
from scrapy import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

import settings as my_settings
from items import BoutsScrapedItem

sys.path.append('/Users/charlespierse/PycharmProjects/UFC_Fight_Predictor/fightPredictor/Scrapers/Bouts_Scraper/bouts_scraped/bouts_scraped')


class UFC_Bouts(scrapy.Spider):
    name = "BoutsSpider"  # we use this name to run 'scrapy crawl <name>' in terminal

    def start_requests(self):
        start_urls = [
            'http://ufcstats.com/statistics/events/completed?page=all'
            # 'http://ufcstats.com/statistics/events/completed?page=all'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        fight_links = response.xpath("//td[@class='b-statistics__table-col']//a/@href").extract()
        for link in fight_links:
            yield scrapy.Request(link, callback=self.parse_bouts)

    def parse_bouts(self, response):
        sel = Selector(response)
        event_name = sel.xpath('//span[@class="b-content__title-highlight"]/text()').extract()[0]
        event_date = sel.xpath('//li[1][@class="b-list__box-list-item"]/text()').extract()[1]
        event_attendance = sel.xpath('//li[3][@class="b-list__box-list-item"]/text()').extract()[1]

        for tr in sel.xpath('//tbody[@class="b-fight-details__table-body"]/tr'):
            # could have written a nice loop to make this neater and less typing intensive, oh well
            bout_item = BoutsScrapedItem()
            bout_item['event_name'] = event_name.strip()
            bout_item['event_date'] = event_date.strip().replace(",", "")
            bout_item['event_attendance'] = int(event_attendance.strip().replace(",", ""))
            bout_item['fighter1'] = tr.xpath('td[2]//a/text()').extract()[0].strip()
            bout_item['fighter2'] = tr.xpath('td[2]//a/text()').extract()[1].strip()
            bout_item['str_stat_f1'] = int(tr.xpath('td[3]//p/text()').extract()[0].strip())
            bout_item['str_stat_f2'] = int(tr.xpath('td[3]//p/text()').extract()[1].strip())
            bout_item['td_stat_f1'] = int(tr.xpath('td[4]//p/text()').extract()[0].strip())
            bout_item['td_stat_f2'] = int(tr.xpath('td[4]//p/text()').extract()[1].strip())
            bout_item['sub_stat_f1'] = int(tr.xpath('td[5]//p/text()').extract()[0].strip())
            bout_item['sub_stat_f2'] = int(tr.xpath('td[5]//p/text()').extract()[1].strip())
            bout_item['pass_stat_f1'] = int(tr.xpath('td[6]//p/text()').extract()[0].strip())
            bout_item['pass_stat_f2'] = int(tr.xpath('td[6]//p/text()').extract()[1].strip())
            bout_item['weight_class'] = tr.xpath('td[7]//p/text()').extract()[0].strip()
            bout_item['win_method_type'] = tr.xpath('td[8]//p/text()').extract()[0].strip()
            bout_item['win_method_finish'] = tr.xpath('td[8]//p/text()').extract()[1].strip()
            bout_item['round'] = int(tr.xpath('td[9]//p/text()').extract()[0].strip())
            bout_item['time'] = float(tr.xpath('td[10]//p/text()').extract()[0].strip().replace(":", "."))
            bout_item['winner'] = bout_item['fighter1']

            yield bout_item


crawler_settings = Settings()
crawler_settings.setmodule(my_settings)
process = CrawlerProcess(settings=crawler_settings)
process.crawl(UFC_Bouts)
process.start()
