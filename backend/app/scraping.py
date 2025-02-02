import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from typing import List, Dict

from scrapy_playwright.page import PageMethod
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, schemas
import random
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from twisted.internet import reactor
logging.basicConfig(level=logging.INFO)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-GB",
}

class HotelItem(Item):
    name = Field()
    image_url = Field()
    price = Field()
    star_rating = Field()
    booking_url = Field()
    source = Field()


class BookingSpider(CrawlSpider):
    name = "booking"
    allowed_domains = ["booking.com"]


    def __init__(self, city=None, min_price=None, max_price=None, star_rating=None, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.min_price = min_price
        self.max_price = max_price
        self.star_rating = star_rating
        self.check_in = datetime.today().strftime('%Y-%m-%d')
        self.check_out = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        self.logger.info(f"Initialized BookingSpider for city: {city}, "
                         f"price range: {min_price}-{max_price}, star rating: {star_rating}")

        self.start_urls = [f"https://www.booking.com/searchresults.en-gb.html?ss={self.city}"
                           f"&order=popularity&nflt=class%3D{self.star_rating}"
                           f"%3Bprice%3DBDT-{int(self.min_price)}-{int(self.max_price)}-1"
                           f"&checkin={self.check_in}&checkout={self.check_out}"]

        self.rules = (
          Rule(LinkExtractor(restrict_css = ".bui-pagination__item.bui-pagination__item--next a"),
               callback="parse", follow=True),
        )

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(f"Starting request for URL: {url}")
            yield scrapy.Request(url=url,
                                 meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_coroutines": [
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_timeout", 20000),
                ],
            }, headers=headers, callback=self.parse, errback=self.errback)


    def parse(self, response):
        hotel_cards = response.css("div[data-testid='property-card']")
        self.logger.info(f"Length of hotel cards: {len(hotel_cards)}")
        for card in hotel_cards:
            try:
                name = card.css('div[data-testid="title"]::text').get()
                image_url = card.css('img[data-testid="image"]::attr(src)').get()
                price_text = card.css('span[data-testid="price-and-discounted-price"]::text').get()
                price = float(re.search(r'\d[\d,]*', price_text).group().replace(',', '')) \
                    if re.search(r'\d[\d,]*', price_text) else 0.0
                star_rating_text = card.css('div[data-testid="review-score"] div::text').get()
                star_rating = float(re.search(r'\d+\.\d+', star_rating_text).group()) if star_rating_text else 0.0
                booking_url = card.css('a[data-testid="availability-cta-btn"]::attr(href)').get()
                self.logger.info(f"Extracted hotel card: {name}, {image_url}, {price}, {star_rating}, {booking_url}")
                if name and image_url and price and star_rating and booking_url:
                    item = HotelItem(
                      name=name,
                      image_url=image_url,
                      price=price,
                      star_rating=star_rating,
                      booking_url=booking_url,
                      source='booking.com',
                    )
                    yield item
            except Exception as e:
                self.logger.error(f"Error processing hotel card: {e}")

    def errback(self, failure):
        self.logger.error(f"Error processing URL: {failure.request.url}. {failure.getErrorMessage()}")


class AgodaSpider(scrapy.Spider):
    pass


def scrape_hotels(city: str, min_price: float, max_price: float, star_rating: int, db: Session) -> List[schemas.HotelResponse]:
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "hotels.json": {"format": "json", "overwrite": True},
            },

           'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 100,
            },
           'HTTPPROXY_AUTH_ENCODING': 'utf-8',
           'PROXY_URL': "http://188.166.229.121:80",
            "RETRY_ENABLED": True,
            "RETRY_TIMES": 2,
            "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 403, 404, 408],
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "CONCURRENT_REQUESTS": 16,
            "LOG_LEVEL": "INFO",
        }
    )
    process.crawl(BookingSpider, city=city, min_price=min_price, max_price=max_price, star_rating=star_rating)
    process.crawl(AgodaSpider, city=city, min_price=min_price, max_price=max_price, star_rating=star_rating)

    process.start()

    hotel_data = []
    with open("hotels.json", "r") as f:
        import json
        items = json.load(f)
        hotel_map: Dict[str, schemas.HotelResponse] = {}

        for item in items:
            hotel_name = item['name']
            if hotel_name in hotel_map:
                hotel_map[hotel_name].prices.append(schemas.PriceBase(price=item['price'], source=item['source']))
            else:
                hotel_map[hotel_name] = schemas.HotelResponse(
                    name=item['name'],
                    image_url=item['image_url'],
                    star_rating=item['star_rating'],
                    city = city,
                    booking_url=item['booking_url'],
                    id = random.randint(1,100000000),
                    prices = [schemas.PriceBase(price=item['price'], source=item['source'])]
                )

        for hotel_name in hotel_map:
            hotel = hotel_map[hotel_name]
            db_hotel = db.query(models.Hotel).filter(models.Hotel.name == hotel.name).first()
            if not db_hotel:
                db_hotel = models.Hotel(
                    name=hotel.name,
                    image_url=hotel.image_url,
                    star_rating=hotel.star_rating,
                    city = city,
                    booking_url=hotel.booking_url,
                )
                db.add(db_hotel)
                db.commit()
                db.refresh(db_hotel)
            for price in hotel.prices:
                db_price = models.Price(hotel_id=db_hotel.id, source = price.source, price=price.price)
                db.add(db_price)
            db.commit()
            hotel_data.append(hotel)
        return hotel_data
