DOWNLOADER_MIDDLEWARES = {
    'scraperexample.middlewares.custom_headers.RandomizeFingerprintMiddleware': 600,
}
ITEM_PIPELINES = {'scraperexample.pipelines.save_page.SavePage': 1}
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
