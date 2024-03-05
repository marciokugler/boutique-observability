#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0


import json
import os
import random
import uuid
import time
from locust import HttpUser, task, between, TaskSet

from locust_plugins.users.playwright import PlaywrightUser, pw, PageWithRetry, event


from playwright.async_api import Route, Request
from locust import HttpUser, run_single_user, task
import logging
from http.client import HTTPConnection
import sys


categories = [
    "binoculars",
    "telescopes",
    "accessories",
    "assembly",
    "travel",
    "books",
    None,
]

products = [
    "0PUK6V6EV0",
    "1YMWWN1N4O",
    "2ZYFJ3GM2N",
    "66VCHSJNUP",
    "6E92ZMYYFZ",
    "9SIQT8TOJO",
    "L9ECAV7KIM",
    "LS4PSXUNUM",
    "OLJCESPC7Z",
    "HQTGWGPNH4",
]





HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class WebsiteUser(HttpUser):
    wait_time = between(10, 10)

    @task(1)
    def index(self):
        self.client.get("/")

    #@task(2)
    #def browse_product(self):
    #    self.client.get("/product/" + random.choice(products))

    @task(3)
   
    def add_to_cart(self):
        product = random.choice(products)
        self.client.get(("/product/" + product), )
        self.client.post("/cart", {
            'product_id': product,
            'quantity': random.choice([1,2,3,4,5,10])})
    
    #@task(4)
    #def view_cart(self):
    #    self.client.get("/cart")
        
    @task(5)
    def checkout(self):
        self.add_to_cart()
        self.client.post("/cart/checkout", {
            'email': 'locust-user@example.com',
            'street_address': '1600 Amphitheatre Parkway',
            'zip_code': '94043',
            'city': 'Mountain View',
            'state': 'CA',
            'country': 'United States',
            'credit_card_number': '4432-8015-6152-0454',
            'credit_card_expiration_month': '1',
            'credit_card_expiration_year': '2039',
            'credit_card_cvv': '672',
        })

    
    def on_start(self):
        self.index()


browser_traffic_enabled = os.environ.get("LOCUST_BROWSER_TRAFFIC_ENABLED", "").lower() in ("true", "yes", "on")
browser_traffic_enabled = True
if browser_traffic_enabled:
    class WebsiteBrowserUser(PlaywrightUser):
        headless = True  # to use a headless browser, without a GUI
        
        @task
        @pw
        async def open_cart_page_and_change_currency(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                await page.route(('**/*', add_baggage_header), )
                await page.goto('/', add_baggage_header, wait_until="domcontentloaded", )
                
                await page.goto("/cart", wait_until="domcontentloaded", )
                
                await page.select_option('[name="currency_code"]', 'CHF')
                
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass

        @task
        @pw
        async def add_product_to_cart_and_purchase(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                #Go to root website
                await page.route('**/*', add_baggage_header)
                await page.goto('/', add_baggage_header, wait_until="domcontentloaded", )
                
                #Click on the Sunglasses category
                await page.click('p:has-text("Sunglasses")', wait_until="domcontentloaded", )
                
                #Add to Cart
                await page.click('button:has-text("Add To Cart")', wait_until="domcontentloaded", )
                
                #Place order
                await page.click('button:has-text("Place Order")', wait_until="domcontentloaded", )
                
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass


async def add_baggage_header(route: Route, request: Request):
    headers = {
        **request.headers,
        'baggage': 'synthetic_request=true'
    }
    await route.continue_(headers=headers)
