# -*- coding: utf-8 -*-
import scrapy, dateparser

class BossCatsSpider(scrapy.Spider):
  name = 'bossCats'
  allowed_domains = ['boss.az']
  start_urls = ['http://boss.az']

  def parse(self, response):
    # create empty dict
    categories = [];
    sub_categories = [];

    # for each option in categories
    for cat in response.xpath('//select[@id="search_category_id"]/option[contains(@value, "")]'):
      # get category name
      cat_name  = cat.xpath('.//text()').get();
      # get category id
      cat_id = cat.xpath('.//@value').get();
      # create category dict
      cat_dict = {
        "id":cat_id,
        "cat_name": cat_name.strip("— ")
      }

      # if option is main category
      if "— " not in cat_name:
        # if already have sub_categories then add to category array
        if len(sub_categories) != 0:
          # create new key for dict to add sub_categories
          cat_main_dict['sub_categories'] = sub_categories;
          # add new dictionary to categories array
          categories.append(cat_main_dict);
          # remove all elements of sub_categories
          sub_categories = [];
        cat_main_dict = cat_dict
      else:
        sub_categories.append(cat_dict);

    # create new key for dict to add sub_categories
    cat_main_dict['sub_categories'] = sub_categories;
    # add new dictionary to categories array
    categories.append(cat_main_dict);

    yield {
      'categories': categories
    }
