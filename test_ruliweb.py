from crawler import RuliwebCrawler, URL, KEY
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

crawler = RuliwebCrawler(URL, KEY)
crawler.crawl()
