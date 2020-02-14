import scrapy
from enum import Enum


class Month(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


class EarlyMidLate(Enum):
    early = 5
    mid = 15
    late = 25


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)


class TourismSpider(scrapy.Spider):
    name = "tour"
    start_urls = [
        'https://weatherspark.com/y/41864/Average-Weather-in-Birmingham-United-Kingdom-Year-Round',
        'https://weatherspark.com/y/81180/Average-Weather-in-Neunkirchen-Austria-Year-Round'
    ]

    def parse(self, response):
        p = response.css(
            'div.Section-body p')[1].css('em').css("::text").getall()
        t = response.css(
            'div.Section-body p')[0].css('em').css("::text").getall()

        celsius = []

        for f in t:
            if f.endswith('F'):
                c = int(f[:-2])
                #print("c "+str(c))
                d = (c-32) * 5/9
                #print("d "+str(d))
                celsius.append(round(d))
            else:
                celsius.append(int(f[:-2]))

        city = response.css("ol.breadcrumb li")
        city = city[len(city)-1]

        coordinates = response.css('div.Section-body')[10].css('p::text').get().split(",")[1:3]
        lat = coordinates[0].split(' deg latitude')[0].split(' ')[-1]
        lon = coordinates[1].split(' deg longitude')[0].split(' ')[-1]
        # print("WILMA: touriepi/y/")
        yield {
            "iso": response.css("ol.breadcrumb li a")[1].css("::attr(href)").get().split('/')[2],
            "country": response.css("ol.breadcrumb li")[1].css("::text")[1].get(),
            "city": city.css("::text").get().strip(),
            "latitude": float(lat),
            "longitude": float(lon),
            "day_from": EarlyMidLate[p[0].split(' ')[0]].value,
            "day_to": EarlyMidLate[p[1].split(' ')[0]].value,
            "month_from": Month[p[0].split(' ')[1]].value,
            "month_to": Month[p[1].split(' ')[1]].value,
            "temp_typical_low": celsius[0],
            "temp_typical_high": celsius[1]}


class LinkSpider(scrapy.Spider):
    name = "links"
    start_urls = [
        'https://weatherspark.com/countries',

    ]

    def parse(self, response):
        a = response.css("body > div.container > div.row li a")

        for l in a.css("::attr(href)"):
            b = l.get().split('/')
            #if ((b[2]=='US' and (len(b) > 4)) or (b[2]!='US' and (len(b)>3))):
            if (len(b)>3):
                continue

            if (b[1] == 'y'):
                # print("WILMA: /y/")
                yield scrapy.Request(response.urljoin(l.get()), callback=self.touriparse)
                # response.urljoin(l.get())
            else:
                # print("WILMA: go countriesparse")
                next_page = l.get()
                if next_page is not None:
                    next_page = response.urljoin(next_page)
                    yield scrapy.Request(next_page, callback=self.countriesparse)

    def countriesparse(self, response):
        a = response.css("body > div.container > div.row")[1].css("li a")

        for l in a.css("::attr(href)"):
            b = l.get().split('/')[1]
            if (b == 'y'):
                # print("WILMA: go touriesparse")
                yield scrapy.Request(response.urljoin(l.get()), callback=self.touriparse)

    def touriparse(self, response):
        p = response.css(
            'div.Section-body p')[1].css('em').css("::text").getall()
        t = response.css(
            'div.Section-body p')[0].css('em').css("::text").getall()

        celsius = []

        for f in t:
            if f.endswith('F'):
                c = int(f[:-2])
                d = (c-32) * 5/9
                celsius.append(round(d))
            else:
                celsius.append(int(f[:-2]))

        city = response.css("ol.breadcrumb li")
        city = city[len(city)-1]

        sectionBodys = response.css('div.Section-body') #[10].css('p::text').get().split(",")
        coordinates = []

        for s in sectionBodys:
            text = s.css('p::text').get()
            if "longitude" in text:
                coordinates = text.split(",")

        if len(coordinates) == 0 :
            print("no coordinates")

        lat = coordinates[1].split(' deg latitude')[0].split(' ')[-1]
        lon = coordinates[2].split(' deg longitude')[0].split(' ')[-1]

        # print("WILMA: touriepi/y/")
        yield {
            "iso": response.css("ol.breadcrumb li a")[1].css("::attr(href)").get().split('/')[2],
            "country": response.css("ol.breadcrumb li")[1].css("::text")[1].get(),
            "city": city.css("::text").get().strip(),
            "latitude": float(lat),
            "longitude": float(lon),
            "day_from": EarlyMidLate[p[0].split(' ')[0]].value,
            "day_to": EarlyMidLate[p[1].split(' ')[0]].value,
            "month_from": Month[p[0].split(' ')[1]].value,
            "month_to": Month[p[1].split(' ')[1]].value,
            "temp_typical_low": celsius[0],
            "temp_typical_high": celsius[1]}
