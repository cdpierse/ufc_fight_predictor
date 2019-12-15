from __future__ import absolute_import

import string

import scrapy
from scrapy import Selector
from scrapy.crawler import CrawlerProcess

from fight_scraper.items import FightScraperItem


class Fighters(scrapy.Spider):
    name = "fighterSpider"

    def start_requests(self):
        start_urls = [
            'http://ufcstats.com/statistics/fighters?char=' + letter + '&page=all' for letter in string.ascii_lowercase
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        links = response.xpath(
            "//td[@class ='b-statistics__table-col']//@href").extract()
        for link in links:
            yield scrapy.Request(link, callback=self.parse_fighter)

    def parse_fighter(self, response):
        sel = Selector(response)
        fighter_item = FightScraperItem()
        fighter_item['fighter_name'] = sel.xpath(
            "//span[@class='b-content__title-highlight']//text()").extract()[0].strip()
        fighter_item['fighter_record'] = sel.xpath(
            "//span[@class='b-content__title-record']//text()").extract()[0].strip()
        for item in response.xpath('//ul[@class="b-list__box-list"]'):
            try:
                fighter_item['height'] = item.xpath(
                    'li[1]//text() ').extract()[2].strip().replace("\\", "")
            except Exception:
                fighter_item['height'] = None
            try:
                fighter_item['weight'] = int(item.xpath(
                    'li[2]//text()').extract()[2].replace("lbs.", ""))
            except Exception:
                fighter_item['weight'] = None
            try:
                fighter_item['reach'] = int(item.xpath(
                    'li[3]//text()').extract()[2].replace('"', ''))
            except Exception:
                fighter_item['reach'] = None

            fighter_item['stance'] = item.xpath(
                'li[4]//text()').extract()[2].strip()
            fighter_item['date_of_birth'] = item.xpath(
                'li[5]//text()').extract()[2].strip().replace(",", "")

        for item in response.xpath('//div[@class="b-list__info-box-left"]//ul'):
            fighter_item['slpm'] = float(item.xpath(
                'li[1]//text() ').extract()[2].strip())
            fighter_item['strike_acc'] = int(item.xpath(
                'li[2]//text()').extract()[2].replace("%", ""))
            fighter_item['sapm'] = float(
                item.xpath('li[3]//text()').extract()[2])
            fighter_item['strike_def'] = float(item.xpath(
                'li[4]//text()').extract()[2].replace("%", ""))

        for item in response.xpath('//div[@class="b-list__info-box-right b-list__info-box_style-margin-right"]//ul'):
            fighter_item['td_avg'] = float(
                item.xpath('li[2]//text()').extract()[2])
            fighter_item['td_acc'] = int(item.xpath(
                'li[3]//text()').extract()[2].replace("%", ""))
            fighter_item['td_def'] = int(item.xpath(
                'li[4]//text()').extract()[2].replace("%", ""))
            fighter_item['sub_avg'] = float(
                item.xpath('li[5]//text()').extract()[2])

        yield fighter_item


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(Fighters)
    process.start() 
