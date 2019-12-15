# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import NotConfigured
import sqlite3
import os
from pathlib import Path


class FightScraperPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        os.chdir("..")
        # db_dir = os.getcwd()
        # print(os.getcwd())
        # print(f"the db dir is {db_dir}")
        print(os.getcwd())
        self.conn = sqlite3.connect(os.path.join("db", "scraped_data.db"))
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS fighters""")
        self.curr.execute("""
        create table fighters(
            date_of_birth TEXT, 
            fighter_name TEXT,
            fighter_record TEXT, 
            height TEXT,
            reach INTEGER,
            sapm INTEGER, 
            slpm INTEGER,
            stance TEXT,
            strike_acc INTEGER,
            strike_def INTEGER,
            sub_avg INTEGER,
            td_acc INTEGER,
            td_avg INTEGER, 
            td_def INTEGER,
            weight INTEGER
        )
        
        """)

    def store_db(self, item):
        self.curr.execute(""" INSERT INTO fighters values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            item['date_of_birth'],
            item['fighter_name'],
            item['fighter_record'],
            item['height'],
            item['reach'],
            item['sapm'],
            item['slpm'],
            item['stance'],
            item['strike_acc'],
            item['strike_def'],
            item['sub_avg'],
            item['td_acc'],
            item['td_avg'],
            item['td_def'],
            item['weight']

        ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        return item
