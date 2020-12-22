# -*- coding: utf-8 -*-
import scrapy, dateparser

class BossJobsSpider(scrapy.Spider):
  name = 'bossJobs'
  allowed_domains = ['boss.az']
  start_urls = ['http://boss.az/vacancies']

  def parse(self, response):
    for jobs in response.xpath('//div[@class="results-i"]'):
      url = jobs.xpath(".//div[@class='results-i-salary-and-link']/a[@class='results-i-link']/@href").get()
      yield scrapy.Request(response.urljoin(url), callback=self.parse_detail)

    next_page = response.xpath('//span[@class="next"]/a/@href').get()

    if next_page is not None:
      yield scrapy.Request(response.urljoin(next_page))

  def decode_email(self, e):
    de = ""
    k = int(e[:2], 16)
    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)
    return de

  def parse_detail(self, response):
    # get start date and parse to correct string
    start_date_str = response.xpath('//div[@class="bumped_on params-i-val"]/text()').get()
    start_date = dateparser.parse(start_date_str).strftime('%d/%m/%Y')
    # get end date and parse to correct string
    end_date_str = response.xpath('//div[@class="expires_on params-i-val"]/text()').get()
    end_date = dateparser.parse(end_date_str).strftime('%d/%m/%Y')
    # get candidate ages
    age = response.xpath('//div[@class="age params-i-val"]/text()').re("\d+")
    # get candidate work experience
    experience = response.xpath('//div[@class="experience params-i-val"]/text()').re("\d+")
    # get salary
    salary = response.xpath('//span[@class="post-salary salary"]/text()').re("\d+");
    # get encoded email
    encoded_email = response.xpath('//div[@class="email params-i-val"]/a/@href').get().split("#")[-1]
    email = self.decode_email(encoded_email)

    # yield values
    yield {
      'id': response.xpath('//div[@class="post-header-secondary"]/text()').re("\d+")[1],
      'url': response.url,
      'title': response.xpath('//h1[@class="post-title"]/text()').get(),
      'city': response.xpath('//div[@class="region params-i-val"]/text()').get(),
      'salary': {
        'min': (salary[0] if len(salary) > 0 else None), # if has atleast 1 item then get first as min
        'max': (salary[1] if len(salary) > 1 else None) # if has atleast 2 items then get second as max
      },
      'age': {
        'min': (age[0] if len(age) > 0 else None), # if has atleast 1 item then get first as min
        'max': (age[1] if len(age) > 1 else None) # if has atleast 2 items then get second as max
      },
      'experience': {
        "min": (experience[0] if len(experience) > 0 else None), # if has atleast 1 item then get first as min
        "max": (experience[1] if len(experience) > 1 else None) # if has atleast 2 items then get second as max
      },
      'start_date': start_date,
      'end_date': end_date,
      'contact_person': response.xpath('//div[@class="contact params-i-val"]/text()').get(),
      'company': {
        'id':  response.xpath('//a[@class="post-company"]/@href').get().split("=")[-1],
        'url': response.xpath('//a[@class="post-company"]/@href').get(),
        'title': response.xpath('//a[@class="post-company"]/text()').get()
      },
      'phones': response.xpath('//a[@class="phone"]/text()').extract(),
      'email': email,
      'description': "".join(response.xpath('//dd[@class="job_description params-i-val"]/p/text()').extract()),
      'requirements': "".join(response.xpath('//dd[@class="requirements params-i-val"]/p/text()').extract()),
      'category': {
          'id': response.xpath('//div[@class="breadcrumbs"]/a/@href').get().split('=')[-1],
          'name':response.xpath('//div[@class="breadcrumbs"]/a/text()').get(),
          'sub_category': {
            'id': response.xpath('//div[@class="breadcrumbs"]/a[2]/@href').get().split('=')[-1],
            'name':response.xpath('//div[@class="breadcrumbs"]/a[2]/text()').get(),
          }
      }
    }
