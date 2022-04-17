from datetime import date
import os
import scrapy
import pandas as pd


class HabrbotSpider(scrapy.Spider):
    file_path = os.path.join('', 'history.csv')
    name = 'habrbot'
    allowed_domains = ['career.habr.com']
    start_urls = ['https://career.habr.com/salaries']

    def parse(self, response):
        self.log('crawling started...')
        summary_str = response.css('div.summ::text').get()
        summary = summary_str.replace('руб. в месяц', '').replace(' ', '')
        self.log(summary)
        df = pd.read_csv(self.file_path) if os.path.exists(self.file_path) else pd.DataFrame([], columns=['salary', 'date'])
        df = df.append({'salary': summary, 'date': date.today()}, ignore_index=True)
        df.to_csv(self.file_path, index=False)
        self.log('crawling completed')
