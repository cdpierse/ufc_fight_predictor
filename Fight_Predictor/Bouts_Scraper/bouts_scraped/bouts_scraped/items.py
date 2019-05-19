# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class BoutsScrapedItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    event_name = Field()
    event_date = Field()
    event_attendance = Field()
    fighter1 = Field()
    fighter2 = Field()
    str_stat_f1 = Field()
    str_stat_f2 = Field()
    td_stat_f1 = Field()
    td_stat_f2 = Field()
    sub_stat_f1 = Field()
    sub_stat_f2 = Field()
    pass_stat_f1 = Field()
    pass_stat_f2 = Field()
    weight_class = Field()
    win_method_type = Field()
    win_method_finish = Field()
    round = Field()
    time = Field()
    winner = Field()
    pass
