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

from opentelemetry import context, baggage, trace
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from playwright.async_api import Route, Request

exporter = OTLPMetricExporter(insecure=True)
set_meter_provider(MeterProvider([PeriodicExportingMetricReader(exporter)]))

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

# Instrumenting manually to avoid error with locust gevent monkey
Jinja2Instrumentor().instrument()
RequestsInstrumentor().instrument()
SystemMetricsInstrumentor().instrument()
URLLib3Instrumentor().instrument()

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



people_file = open('people.json')
people = json.load(people_file)




products = [
    '0PUK6V6EV0',
    '1YMWWN1N4O',
    '2ZYFJ3GM2N',
    '66VCHSJNUP',
    '6E92ZMYYFZ',
    '9SIQT8TOJO',
    'L9ECAV7KIM',
    'LS4PSXUNUM',
    'OLJCESPC7Z']

def index(l):
    l.client.get("/")

def setCurrency(l):
    currencies = ['EUR', 'USD', 'JPY', 'CAD']
    l.client.post("/setCurrency",
        {'currency_code': random.choice(currencies)})

def browseProduct(l):
    l.client.get("/product/" + random.choice(products))

def viewCart(l):
    l.client.get("/cart")

def addToCart(l):
    product = random.choice(products)
    l.client.get("/product/" + product)
    l.client.post("/cart", {
        'product_id': product,
        'quantity': random.choice([1,2,3,4,5,10])})

def checkout(l):
    addToCart(l)
    l.client.post("/cart/checkout", {
        'email': 'someone@example.com',
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


def on_start(l):
    ctx = baggage.set_baggage("synthetic_request", "true")
    context.attach(ctx)
    l.index()


browser_traffic_enabled = os.environ.get("LOCUST_BROWSER_TRAFFIC_ENABLED", "").lower() in ("true", "yes", "on")

if browser_traffic_enabled:
    class WebsiteBrowserUser(PlaywrightUser):
        headless = True  # to use a headless browser, without a GUI

        @task
        @pw
        async def open_cart_page_and_change_currency(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                await page.route('**/*', add_baggage_header)
                await page.goto('/', add_baggage_header, wait_until="domcontentloaded")
                time.sleep(5)
                await page.goto("/cart", wait_until="domcontentloaded")
                time.sleep(5)
                await page.select_option('[name="currency_code"]', 'CHF')
                time.sleep(5)
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass

        @task
        @pw
        async def add_product_to_cart(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                #Go to root website
                await page.route('**/*', add_baggage_header)
                await page.goto('/', add_baggage_header, wait_until="domcontentloaded")
                time.sleep(5)
                #Click on the Sunglasses category
                await page.click('p:has-text("Sunglasses")', wait_until="domcontentloaded")
                time.sleep(5)
                #Add to Cart
                await page.click('button:has-text("Add To Cart")', wait_until="domcontentloaded")
                time.sleep(5)
                #Place order
                await page.click('button:has-text("Place Order")', wait_until="domcontentloaded")
                time.sleep(5)
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass


async def add_baggage_header(route: Route, request: Request):
    headers = {
        **request.headers,
        'baggage': 'synthetic_request=true'
    }
    await route.continue_(headers=headers)


class UserBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {index: 1,
        setCurrency: 2,
        browseProduct: 10,
        addToCart: 2,
        viewCart: 3,
        checkout: 1}

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)