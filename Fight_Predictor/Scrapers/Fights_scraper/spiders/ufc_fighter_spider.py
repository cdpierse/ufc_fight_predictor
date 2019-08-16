import sys
sys.path.append('/Users/charlespierse/PycharmProjects/UFC_Fight_Predictor/Fight_Predictor/Scrapers/Fights_scraper/')


import scrapy
import string
from scrapy import Selector
from items import FighterScraperItem
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
import settings as my_settings


class UFC_Fighter(scrapy.Spider):
    name = "FighterSpider" # we use this name to run 'scrapy crawl <name>' in terminal

    def start_requests(self):
        start_urls = [
            'http://ufcstats.com/statistics/fighters?char='+ letter +'&page=all' for letter in string.ascii_lowercase
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        fighter_links = response.xpath("//td[@class ='b-statistics__table-col']//@href").extract()
        for link in fighter_links:
            yield scrapy.Request(link, callback=self.parse_fighter)

    def parse_fighter(self,response):
        sel = Selector(response)
        fighter_item = FighterScraperItem()
        fighter_item['fighter_name'] = sel.xpath("//span[@class='b-content__title-highlight']//text()").extract()[0].strip()
        # TODO extract only the numbers from the record string
        fighter_item['fighter_record'] = sel.xpath("//span[@class='b-content__title-record']//text()").extract()[0].strip()
        for item in response.xpath('//ul[@class="b-list__box-list"]'):
            try:
                fighter_item['height'] = item.xpath('li[1]//text() ').extract()[2].strip().replace("\\","")
            except:
                fighter_item['height'] = None
            try:
                fighter_item['weight'] = int(item.xpath('li[2]//text()').extract()[2].replace("lbs.", ""))
            except:
                fighter_item['weight'] = None
            try:
                fighter_item['reach'] = int(item.xpath('li[3]//text()').extract()[2].replace('"',''))
            except:
                fighter_item['reach'] = None

            fighter_item['stance'] = item.xpath('li[4]//text()').extract()[2].strip()
            fighter_item['date_of_birth'] = item.xpath('li[5]//text()').extract()[2].strip().replace(",","")

        for item in response.xpath('//div[@class="b-list__info-box-left"]//ul'):
            fighter_item['slpm'] = float(item.xpath('li[1]//text() ').extract()[2].strip())
            fighter_item['strike_acc'] = int(item.xpath('li[2]//text()').extract()[2].replace("%",""))
            fighter_item['sapm'] = float(item.xpath('li[3]//text()').extract()[2])
            fighter_item['strike_def'] = float(item.xpath('li[4]//text()').extract()[2].replace("%",""))

        for item in response.xpath('//div[@class="b-list__info-box-right b-list__info-box_style-margin-right"]//ul'):
            fighter_item['td_avg']= float(item.xpath('li[2]//text()').extract()[2])
            fighter_item['td_acc']= int(item.xpath('li[3]//text()').extract()[2].replace("%",""))
            fighter_item['td_def']= int(item.xpath('li[4]//text()').extract()[2].replace("%", ""))
            fighter_item['sub_avg']= float(item.xpath('li[5]//text()').extract()[2])

        yield fighter_item

crawler_settings = Settings()
crawler_settings.setmodule(my_settings)
process = CrawlerProcess(settings=crawler_settings)
process.crawl(UFC_Fighter)
process.start()




