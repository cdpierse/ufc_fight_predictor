# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import NotConfigured
import sqlite3
import os
from pathlib import Path


class BoutScraperPipeline(object):

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
        self.curr.execute("""DROP TABLE IF EXISTS bouts""")
        self.curr.execute("""
        create table bouts(
            event_date TEXT, 
            event_name TEXT,
            fighter1 TEXT, 
            fighter2 TEXT,
            pass_stat_f1 INTEGER,
            pass_stat_f2 INTEGER, 
            round_ INTEGER,
            str_stat_f1 INTEGER,
            str_stat_f2 INTEGER,
            sub_stat_f1 INTEGER,
            sub_stat_f2 INTEGER,
            td_stat_f1 INTEGER,
            td_stat_f2 INTEGER, 
            time INTEGER,
            weight_class TEXT,
            win_method_finish TEXT,
            win_method_type TEXT,
            winner TEXT
        )
        
        """)

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.curr.execute(""" INSERT INTO BOUTS values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            item['event_date'],
            item['event_name'],
            item['fighter1'],
            item['fighter2'],
            item['pass_stat_f1'],
            item['pass_stat_f2'],
            item['round_'],
            item['str_stat_f1'],
            item['str_stat_f2'],
            item['sub_stat_f1'],
            item['sub_stat_f2'],
            item['td_stat_f1'],
            item['td_stat_f2'],
            item['time'],
            item['weight_class'],
            item['win_method_finish'],
            item['win_method_type'],
            item['winner']

        ))

        self.conn.commit()
