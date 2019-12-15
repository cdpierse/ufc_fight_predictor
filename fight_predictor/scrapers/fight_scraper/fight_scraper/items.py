# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class FightScraperItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fighter_name = Field()
    fighter_record = Field()
    height = Field()
    weight = Field()
    reach = Field()
    stance = Field()
    date_of_birth = Field()
    slpm = Field()  # strikes landed per min stat
    td_avg = Field()  # takedown average
    strike_acc = Field()  # striking accuracy
    td_acc = Field()  # takedown accuracy
    sapm = Field()  # strikes absorbed per minute
    td_def = Field()  # takedown defence
    strike_def = Field()  # striking defence
    sub_avg = Field()  # submission average

