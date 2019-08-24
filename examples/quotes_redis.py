from acrawler import Crawler, ParselItem, Parser, Processors, get_logger
from acrawler.utils import redis_push_start_urls

logger = get_logger("quotes")


class QuoteItem(ParselItem):
    default = {"type": "quote"}
    css = {"author": "small.author::text"}
    xpath = {"text": ['.//span[@class="text"]/text()', lambda s: s.strip("“")[:20]]}


class AuthorItem(ParselItem):
    default = {"type": "author"}
    css = {"name": "h3.author-title::text", "born": "span.author-born-date::text"}


class QuoteCrawler(Crawler):
    config = {
        "LOG_LEVEL": "INFO",
        "MAX_REQUESTS": 16,
        "REDIS_ENABLE": True,
        "REDIS_START_KEY": "acrawler:QuoteCrawler:starturls",
        "REDIS_ITEMS_KEY": "acrawler:QuoteCrawler:items",
        "DOWNLOAD_DELAY": 3,
    }

    middleware_config = {
        "acrawler.handlers.ItemToRedis": 100,
        "acrawler_prometheus.PromExporter": 100,
    }

    main_page = r"quotes.toscrape.com/page/\d+"
    author_page = r"quotes.toscrape.com/author/.*"
    parsers = [
        Parser(
            in_pattern=main_page,
            follow_patterns=[main_page, author_page],
            item_type=QuoteItem,
            css_divider=".quote",
        ),
        Parser(in_pattern=author_page, item_type=AuthorItem),
    ]

    async def parse(self, response):
        yield {"type": "hhh"}


if __name__ == "__main__":
    print("Adding start urls to Redis, key: acrawler:quotes:starturls")
    # start_urls = [
    #     "http://quotes.toscrape.com/page/1/",
    #     "http://quotes.toscrape.com/page/5/",
    #     "http://quotes.toscrape.com/page/10/",
    # ]
    start_urls = [
        "http://quotes.toscrape.com/page/{}/".format(i) for i in range(1, 1000)
    ]
    redis_push_start_urls("acrawler:QuoteCrawler:starturls", start_urls)

    c = QuoteCrawler().run()
    # Crawler always listen to redis and won't finish.
    # This behaviour is determined by acrawler.handlers.CrawlerFinishAddon
