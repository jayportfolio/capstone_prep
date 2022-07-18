import csv, datetime, time, gc, sys, math
import os, random, re, json
import pandas as pd

import scrapy
from scrapy import Selector
from scrapy.crawler import CrawlerProcess  # Import the CrawlerProcess: for running the spider
import scrapy_splash
from scrapy_splash import SplashRequest

sys.path.append('../../globalfunction')  # setting path
import globalfunction.vv as vv  # importing
import globalfunction.pp as pp  # importing

import html2text

target_concurrency = 7

# PAGES_PER_BOROUGH = 3
# PAGES_PER_BOROUGH = 7
PAGES_PER_BOROUGH = 12

DEBUG_ON = True

# MAX_ITEMS = MAX_LISTINGS * 25 * 2
SCRAPED_LISTINGS = -1
SCRAPED_ITEMS = -1
global_min_price = "100000"
multiplier = 0.5
# multiplier = 2
multiplier = 0.1
multiplier = 0

acceptable = vv.VERSION_ACCEPTABLE

NOTHING_YIELDED = True

header_on_meta, header_on_json, first_call = True, True, True
DO_PICKUPS = True
ONLY_PICKUPS = True
DO_LISTINGS = False
DO_ITEMS = False
PICKUP_FROM_TAIL = False  # True

if DO_PICKUPS:
    MAX_ITEMS = vv.MAX_LISTINGS * 25 + 100
else:
    MAX_ITEMS = vv.MAX_LISTINGS * 25 + 20

borough_retrieved_no_data = {}

print_headers = True


class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()


# Create the Spider class
class Splasher_spider(scrapy.Spider):
    name = "splasher_spider"


    custom_settings = {
        #'SOME_SETTING': 'some value',
        #'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.5
        'AUTOTHROTTLE_TARGET_CONCURRENCY': target_concurrency
    }

    print('default settings updated')

    # start_requests method
    def start_requests(self):

        global borough_retrieved_no_data, header_on_meta, header_on_json, SCRAPED_LISTINGS

        #print(pd.DataFrame({k: sys.getsizeof(v) for (k, v) in locals().items()}, index=['Size']).T.sort_values(by='Size', ascending=False).head(4))
        #print(gc.get_threshold())
        #print(gc.get_count())
        gc.collect()
        #print(gc.get_count())

        try:
            pd.read_csv(vv.LISTING_JSON_MODEL_FILE)
            header_on_json = False
        except:
            pass
        try:
            pd.read_csv(vv.LISTING_JSON_META_FILE)
            header_on_meta = False
        except:
            pass

        print(gc.get_count())
        gc.collect()
        print(gc.get_count())
        print(pd.DataFrame({k: sys.getsizeof(v) for (k, v) in locals().items()}, index=['Size']).T.sort_values(by='Size', ascending=False).head(4))

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        if DO_PICKUPS:
            yield from self.pickup_enriching_gaps([vv.LISTING_JSON_MODEL_FILE, vv.LISTING_JSON_MODEL_BID_FILE, vv.LISTING_JSON_MODEL_FAILED])
            yield from self.pickup_enriching_gaps(vv.LISTING_JSON_META_FILE)
            yield from self.pickup_enriching_gaps()
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        if not ONLY_PICKUPS:

            label = "start_requests"

            total_page_count = 0
            for borough_name, borough_code in pp.BOROUGHS.items():
                borough_retrieved_no_data[borough_name] = 0

                print("PAGES_PER_BOROUGH:", PAGES_PER_BOROUGH)
                print(f"max allowed: LISTINGS={vv.MAX_LISTINGS}, ITEMS={MAX_ITEMS}")

                with open(vv.AUDIT_FILE) as f:
                    raw_audit = f.read()
                # print("Data type before reconstruction : ", type(raw_audit))
                # reconstructing the data as a dictionary
                df_audit = json.loads(raw_audit)
                # print("Data type after reconstruction : ", type(df_audit))
                # print(df_audit)

                if df_audit.get(borough_name) and df_audit[borough_name].get("maxxed") and df_audit[borough_name].get("maxxed") == 'MAXXED':
                    print('already reached end of pagination for', borough_name)
                    continue

                if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
                    print(f"00 exceeded max scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS})")
                    return
                if SCRAPED_ITEMS > MAX_ITEMS:
                    print(f"00 B exceeded max scrape: ({SCRAPED_ITEMS} > {MAX_ITEMS})")
                    return

                try:
                    q_minPrice_unrounded = df_audit.get(borough_name).get("min_price")
                    q_minPrice_unrounded = self.price_to_int(q_minPrice_unrounded)

                    for i in range(len(pp.array)):
                        if q_minPrice_unrounded >= pp.array[i]:
                            continue
                        q_minPrice = pp.array[i - 1]
                        break

                    print(q_minPrice)
                except:
                    print(f"didn't find min price for {borough_name}")
                    q_minPrice = global_min_price

                if df_audit.get(borough_name):
                    last_page_was = df_audit.get(borough_name).get("last_page_for_price") - 1
                else:
                    last_page_was = 0

                for page_number in range(max(last_page_was, 0), min(last_page_was + PAGES_PER_BOROUGH, 41)):

                    print(f"Considering borough:{borough_name}, page:{page_number + 1}, price:{q_minPrice}")
                    if borough_retrieved_no_data[borough_name] > 2:
                        print(f"retrieved too many no_datas for {borough_name}, cutting out early")
                        continue

                    if q_minPrice_unrounded > vv.MAX_PRICE:
                        print(f"recorded price {q_minPrice_unrounded} exceeds max price {vv.MAX_PRICE}, cutting out early")
                        continue

                    if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
                        print(f"0 exceeded max scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS})")
                        return


                    index = 24 * page_number

                    print(f"Scraping borough:{borough_name}, page:{page_number + 1}, price:{q_minPrice}")

                    # q_maxPrice = 900000
                    q_maxPrice = vv.MAX_PRICE
                    # q_minPrice = 100000
                    q_ascendingSortType = 1
                    q_propertyTypes = pp.property_types
                    # q_propertyTypes = 'bungalow%2Cterraced'

                    # q_lookback_optional = '&maxDaysSinceAdded=1'
                    q_lookback_optional = ''
                    q_params_optional = pp.params_optional

                    if index == 0:
                        insertIndex = ''
                    elif index != 0:
                        insertIndex = f'&index={index}'

                    listings_url = f"{pp.find_listings_url}{borough_code}&maxPrice={q_maxPrice}&minPrice={q_minPrice}&sortType={q_ascendingSortType}{insertIndex}&propertyTypes={q_propertyTypes}{q_lookback_optional}{q_params_optional}"

                    self.sleep_long_or_short(long_sleep_chance=100,
                                             short_lowbound=0, short_highbound=5,
                                             long_lowbound=10, long_highbound=20, source=label)

                    total_page_count += 1

                    scrapy_splash_request_front = SplashRequest(
                        url=listings_url,
                        callback=self.parse_front,
                        # cb_kwargs=dict(main_url=response.url),
                        cb_kwargs=dict(main_url=listings_url),
                        headers=vv.get_scraper_headers(),

                        args={
                            # optional; parameters passed to Splash HTTP API
                            'wait': 3,
                            # 'wait': 30,
                            # 'wait': self.sleep_long_or_short(skip_sleep=True, source=label + ":SplashRequest"),

                            # 'url' is prefilled from request url
                            # 'http_method' is set to 'POST' for POST requests
                            # 'body' is set to request body for POST requests
                        },
                        # endpoint='render.json',  # optional; default is render.html
                        endpoint='render.html',  # optional; default is render.html
                        splash_url='<url>',  # optional; overrides SPLASH_URL
                        slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                    )

                    scrapy_splash_request_front.cb_kwargs['foo'] = 'bar'  # add more arguments for the callback
                    # add more arguments for the callback
                    scrapy_splash_request_front.cb_kwargs['borough'] = (borough_name, borough_code)
                    scrapy_splash_request_front.cb_kwargs['page_number'] = page_number

                    if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
                        print(f"1 exceeded max scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS})")
                        return
                    # ??? SCRAPED_LISTINGS += 1

                    yield scrapy_splash_request_front
                    print(f"You have scraped page {page_number + 1} from apartment listings.")
                    print("\n")

                    # # code to make them think we are human
                    # self.sleep_long_or_short(long_sleep_chance=100,
                    #                          short_lowbound=0, short_highbound=2,
                    #                          long_lowbound=10, long_highbound=20, source=label + "3")
                    index = index + 24

                print(f'finished scraping (for loop was set to {PAGES_PER_BOROUGH}')

            print("The End!")

    def price_to_int(self, formatted_or_int_value):
        if type(formatted_or_int_value) not in [int, float]:
            formatted_or_int_value = int(formatted_or_int_value.replace(",", ""))
        return formatted_or_int_value

    def pickup_enriching_gaps(self, missable_filename=vv.LISTING_ENRICHED_FILE):
        if print_headers: print("PICKUP_ENRICHING_GAPS")
        global SCRAPED_ITEMS
        if type(missable_filename) == list:
            df_potentially_missing = pd.read_csv(missable_filename[0])
            for i in range(1, len(missable_filename)):
                df_potentially_missing_next = pd.read_csv(missable_filename[i])
                df_potentially_missing = pd.merge(df_potentially_missing, df_potentially_missing_next, on='id', how='outer')
        else:
            df_potentially_missing = pd.read_csv(missable_filename)

        df_listing = pd.read_csv(vv.LISTING_BASIC_FILE)

        id1 = df_listing.columns[0]
        id2 = df_potentially_missing.columns[0]
        # would_be_na = df_potentially_missing.columns[2]
        would_be_na = df_potentially_missing.columns[3]

        # combined_listing_indiv = df_potentially_missing.merge(df_listing, on='ids', how='right', suffixes=('_indiv', '_listing'))
        combined_listing_indiv = df_potentially_missing.merge(df_listing, left_on=id2, right_on=id1, how='right', suffixes=('_missing', '_listing'))
        # select only the rows where the link column is null
        only_listing = combined_listing_indiv[combined_listing_indiv[would_be_na].isna()]
        only_listing_subset = only_listing[[id1, 'Links', 'borough']].set_index(id1)
        only_listing_subset = only_listing_subset[['Links', 'borough']][~only_listing_subset.index.duplicated(keep='last')]

        # print(gc.get_count())
        # gc.collect()
        # print(gc.get_count())
        print(
            pd.DataFrame({k: sys.getsizeof(v) for (k, v) in locals().items()}, index=['Size']).T.sort_values(by='Size', ascending=False).head(4))

        # only_listing_subset = only_listing[['borough', 'Links']]
        del only_listing, combined_listing_indiv, df_listing, df_potentially_missing

        if PICKUP_FROM_TAIL:
            only_listing_subset = only_listing_subset.tail(MAX_ITEMS)

        # print(gc.get_count())
        # gc.collect()
        # print(gc.get_count())
        print(
            pd.DataFrame({k: sys.getsizeof(v) for (k, v) in locals().items()}, index=['Size']).T.sort_values(by='Size', ascending=False).head(4))

        remove_count = -1
        for index, row in only_listing_subset.iterrows():
            bonus_link = row['Links']
            bonus_borough = row['borough']

            with open(vv.REMOVED_FILE) as my_file:
                testsite_array = my_file.readlines()
            testsite_array = [x.strip() for x in testsite_array]

            if bonus_link.replace(pp.unneeded_path_params, "") in testsite_array:
                remove_count += 1
                print(remove_count, ":", bonus_link, "marked as removed already")
                continue

            with open(vv.CORRUPT_FILE) as my_file:
                testsite_array = my_file.readlines()
            testsite_array = [x.strip() for x in testsite_array]

            if bonus_link.replace(pp.unneeded_path_params, "").replace(pp.properties_url, "") in testsite_array:
                remove_count += 1
                print(remove_count, ":", bonus_link, "is corrupt")
                continue

            if SCRAPED_ITEMS < MAX_ITEMS:
                self.sleep_long_or_short(long_sleep_chance=100, short_lowbound=2, short_highbound=7, long_lowbound=30,
                                         long_highbound=60, source='pickup')

                yield from self.splash_pages(bonus_link, None)
                # if True:
                #    return

    # First parsing method
    def parse_front(self, response, main_url, foo, borough, page_number):
        if print_headers: print("PARSE_FRONT")

        global SCRAPED_LISTINGS
        global borough_retrieved_no_data

        label = "parse_front"
        global NOTHING_YIELDED
        NOTHING_YIELDED = False

        borough_name = borough[0]

        if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
            print(f"3 exceeded max listings scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS})")
            return

        potential_model_list = response.css(pp.listings_data).extract()
        for each in potential_model_list:
            if vv.MODEL2 in each:
                page_model = each
                break
        page_model_json = json.loads(page_model.strip().replace(pp.listings_data_intro, ""))

        model_paging = page_model_json[pp.model_paging]

        first = model_paging["first"]
        last = model_paging["last"]
        options = model_paging["options"]
        page = int(model_paging["page"])
        total = model_paging["total"]

        if page > total:
            with open(vv.AUDIT_FILE) as f:
                raw_audit = f.read()
            df_audit = json.loads(raw_audit)
            date_scraped5 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                df_audit[borough_name]["maxxed"] = "MAXXED"
                df_audit[borough_name]["maxxed_date"] = date_scraped5
                with open(vv.AUDIT_FILE, 'w') as convert_file:
                    self.write_json_pretty(convert_file, df_audit)
            except:
                pass

        all_apartment_links = []
        all_description = []
        all_address = []
        all_price = []
        all_codes = []
        date_scraped_list0 = []
        add_info_list = []
        short_description = []
        hold_type = []

        # This gets the number of listings - which I don't actually use
        number_of_listings = int(response.css("span.searchHeader-resultCount::text").extract_first().replace(",", ""))

        try:
            df_indiv_saved2 = pd.read_csv(vv.LISTING_ENRICHED_FILE)
            df_indiv_saved2['ids'] = df_indiv_saved2['ids'].astype('str')
            df_indiv_saved2.set_index("ids", inplace=True)
        except:
            df_indiv_saved2 = None

        apartments = response.css(pp.css_apartments)

        #for quote in response.css('div.quote'):
        for apartment in apartments:
            # course_links = course_blocks.xpath('./a/@href')

            item = QuoteItem()
            # item['text'] = quote.css('span.text::text').extract_first()
            # item['author'] = quote.css('small.author::text').extract_first()
            # item['tags'] = quote.css('div.tags a.tag::text').extract()
            item['tags'] = apartment.css(pp.css_apartment_info).extract()
            yield item

            # append link
            apartment_info = apartment.css(pp.css_apartment_info)
            link = pp.domain_url + apartment_info.attrib['href']
            # all_apartment_links.append(link) relocated

            m = re.finditer(r'.*?/(\d+)#/.*?', link, re.I)
            # all_codes.append(m.__next__())

            match_found = False
            code = None
            for match in m:
                code = match.group(1)
                all_codes.append(code)
                match_found = True
                break

            if not match_found:
                # raise LookupError("didn't find a code match in",link)
                print("no id found /,", "didn't find a code match in", link)
                continue

            all_apartment_links.append(link)

            addresses = apartment_info.css(pp.addresses).extract()
            result = [a for a in addresses if a.strip() != ""]
            all_address.append(", ".join(result))

            # append description
            description = apartment_info.css(pp.description).extract()
            all_description.append(" ".join([d.strip() for d in description]))
            # append price
            try:
                price_raw = apartment.css(pp.price).extract_first()
                price = price_raw.strip().replace("£", "")
                price_filtered = float(price.replace(',', ''))
                valid_price = price_filtered
            except:
                print("can't convert: price is", price, ", link is", response.url)
                valid_price = price

            all_price.append(valid_price)

            # grab the first link on the component (each component has multiple links going to the same place)
            apartment_links = apartment.xpath(pp.xpath_apartment_links)
            indiv_apartment_link = apartment_links.extract_first()
            if not 'http' in indiv_apartment_link:
                indiv_apartment_link = pp.domain_url + indiv_apartment_link

            add_date = apartment.css(pp.add_date).extract_first()
            add_agent = apartment.css(pp.add_agent).extract_first()

            # won't work, that's from the javascript version
            # add_info = apartment.css('div.propertyCard-branchSummary::text').extract_first().strip()
            try:
                add_info = add_date + add_agent
                add_info_list.append(add_info)
            except:
                add_info_list.append("error")

            special_attributes = response.css(pp.special_attribute).extract()
            if len(special_attributes) > 0:
                is_hold = special_attributes[0].contains('hold')
                short_description.extend(special_attributes)

            # get current date and time
            date_scraped = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_scraped_list0.append(date_scraped)

            if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
                print(f"5 exceeded max listings scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS}) {borough_name}")
                continue
            # SCRAPED_LISTINGS += 1
            print(
                f"SCRAPED INDIVIDUAL LISTING ITEM: {SCRAPED_LISTINGS} (SCRAPED ITEMS: {SCRAPED_ITEMS}) <-- {response.url} {borough_name}")

            if DO_ITEMS:
                try:
                    df_indiv_saved2["version"]
                    df_indiv_saved2 = df_indiv_saved2[~df_indiv_saved2.index.duplicated(keep='last')]
                    if code not in df_indiv_saved2.index:
                        debug_print(f"Don't have enriching for this id yet: {code} (page {page_number + 1}), {borough_name} {valid_price}")
                        yield from self.splash_pages(indiv_apartment_link, response)
                    elif (not vv.VERSION_ACCEPTABLE.__contains__(df_indiv_saved2.loc[code]["version"])):
                        debug_print(f"Enriching version is too old for this id: {code} (page {page_number + 1}), {borough_name} {valid_price}")
                        yield from self.splash_pages(indiv_apartment_link, response)
                    else:
                        debug_print(f"already have this id: {code} (page {page_number + 1}), {borough_name} {valid_price}")
                except:
                    print(
                        f"enriched df doesn't exist, or don't have individual listings yet for:{code} (page {page_number + 1}),{borough_name} {valid_price}")
                    yield from self.splash_pages(indiv_apartment_link, response)

        data = {
            "ids": all_codes,
            "Links": all_apartment_links,
            "Address": all_address,
            "Description": all_description,
            "Price": all_price,
            # ,"Station_Prox": stations
            "version": ((vv.VERSION_LATEST + " ") * (len(all_codes))).strip().split(" "),
            "borough": [borough] * (len(all_codes)),
            "referencing_link": [response.url] * len(all_codes),
            "add_info": add_info_list,
            "date_scraped": date_scraped_list0

        }
        if len(all_codes) > 0:
            df_basic = pd.DataFrame.from_dict(data)
            df_basic.set_index("ids", inplace=True)
            try:
                df_saved_basic = pd.read_csv(vv.LISTING_BASIC_FILE)
                df_saved_basic['ids'] = df_saved_basic['ids'].astype('str')
                df_saved_basic.set_index("ids", inplace=True)
                df_combined_basic = pd.concat([df_basic, df_saved_basic])
            except:
                print('reached the exception')
                df_combined_basic = df_basic

            # df_combined_basic.sort_index(inplace=True)
            df_combined_basic = df_combined_basic[~df_combined_basic.index.duplicated(keep='first')]
            try:
                df_combined_basic.to_csv(vv.LISTING_BASIC_FILE, encoding="utf-8", header="true", index=True)
            except:
                print("******** there was some error writing the data! ********")
                print("******** there was some error writing the data! ********")
                print("******** there was some error writing the data! ********")
        else:
            print("66 no ids found")
            borough_retrieved_no_data[borough[0]] += 1

        with open(vv.AUDIT_FILE) as f:
            raw_audit = f.read()
        # print("Data type before reconstruction : ", type(raw_audit))
        # reconstructing the data as a dictionary
        df_audit = json.loads(raw_audit)
        # print("Data type after reconstruction : ", type(df_audit))
        # print(df_audit)
        date_scraped3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # df_audit[borough_name] = {"last_page": pages, "min_value": 5000, "date_scraped": date_scraped3}
        try:
            if df_audit[borough_name]:
                if df_audit[borough_name].get("maxxed") and df_audit[borough_name]["maxxed"] == "MAXXED":
                    print(f'already maxxed for {borough_name}, no need to write to audit')
                elif self.price_to_int(df_audit[borough_name]["min_price"]) < valid_price:
                    df_audit[borough_name]["min_price"] = valid_price
                    df_audit[borough_name]["last_page_for_price"] = 0
                    df_audit[borough_name]["date_scraped"] = date_scraped3
                    df_audit[borough_name]["list_scraped"] = date_scraped3
                    with open(vv.AUDIT_FILE, 'w') as convert_file:
                        self.write_json_pretty(convert_file, df_audit)
                elif self.price_to_int(df_audit[borough_name]["min_price"]) == valid_price and df_audit[borough_name][
                    "last_page_for_price"] < page_number:
                    df_audit[borough_name]["min_price"] = valid_price
                    df_audit[borough_name]["last_page_for_price"] = page_number
                    df_audit[borough_name]["date_scraped"] = date_scraped3
                    df_audit[borough_name]["list_scraped"] = date_scraped3
                    with open(vv.AUDIT_FILE, 'w') as convert_file:
                        self.write_json_pretty(convert_file, df_audit)
            else:
                print('how did we end up here?')
        except:
            print(f"looks like {borough_name} in not in audit")
            detail = {"last_page_for_price": page_number,
                      "min_price": global_min_price,
                      "date_scraped": date_scraped3,
                      "list_scraped": date_scraped3,
                      "item_scraped": ""
                      }
            df_audit[borough_name] = detail

            with open(vv.AUDIT_FILE, 'w') as convert_file:
                self.write_json_pretty(convert_file, df_audit)

        SCRAPED_LISTINGS += 1
        print(f"SCRAPED LISTINGS: {SCRAPED_LISTINGS} (SCRAPED ITEMS: {SCRAPED_ITEMS}) <-- {response.url}")

        if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
            print(f"7 exceeded max listings scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS})")
            return
        if SCRAPED_ITEMS > MAX_ITEMS:
            print(f"7 B exceeded max scrape: ({SCRAPED_ITEMS} > {MAX_ITEMS})")
            return


        if DO_ITEMS:
            for code in all_codes:
                if SCRAPED_LISTINGS > vv.MAX_LISTINGS:
                    print(f"8 exceeded max listings scrape: ({SCRAPED_LISTINGS} > {vv.MAX_LISTINGS}) {borough_name}")
                    return
                try:
                    df_indiv_saved2["version"]
                    df_indiv_saved2 = df_indiv_saved2[~df_indiv_saved2.index.duplicated(keep='last')]
                    if code not in df_indiv_saved2.index:
                        debug_print(f"Don't have enriching for this id yet: {code} (page {page_number + 1}),{borough_name} {valid_price}")
                        yield from self.splash_pages(indiv_apartment_link, response)
                    elif (not vv.VERSION_ACCEPTABLE.__contains__(df_indiv_saved2.loc[code]["version"])):
                        debug_print(f"Enriching version is too old for this id: {code} (page {page_number + 1}),{borough_name} {valid_price}")
                        yield from self.splash_pages(indiv_apartment_link, response)
                    else:
                        debug_print(f"already have this id: {code} (page {page_number + 1}), {borough_name} {valid_price}")
                except:
                    print(
                        f"enriched df doesn't exist, or don't have individual listings yet for:{code} (page {page_number + 1}),{borough_name} {valid_price}")
                    yield from self.splash_pages(indiv_apartment_link, response)

    def write_json_pretty(self, convert_file, df_audit):
        # convert_file.write(json.dumps(df_audit))
        # convert_file.write(json.dumps(df_audit, indent=4, sort_keys=True))
        convert_file.write(json.dumps(df_audit, indent=4))

    def splash_pages(self, indiv_apartment_link, response):
        if print_headers: print("SPLASH_PAGES")
        # yield response.follow(url=indiv_apartment_link, callback=self.parse_pages)

        label = "splashPages(wrapper)"
        yield SplashRequest(url=indiv_apartment_link
                            , callback=self.parse_pages,

                            args={
                                # optional; parameters passed to Splash HTTP API
                                'wait': self.sleep_long_or_short(long_sleep_chance=200, short_lowbound=0,
                                                                 short_highbound=2, long_lowbound=30, long_highbound=90,
                                                                 skip_sleep=True, source=label + ":SplashRequest"),
                                # 'wait': 3

                                # 'url' is prefilled from request url
                                # 'http_method' is set to 'POST' for POST requests
                                # 'body' is set to request body for POST requests
                            },
                            endpoint='render.json',  # optional; default is render.html
                            splash_url='<url>',  # optional; overrides SPLASH_URL
                            slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                            )
        # print('splash request for page: ', indiv_apartment_link)

    # Second parsing method
    def parse_pages(self, response):
        if print_headers: print("PARSE_PAGES")

        global SCRAPED_ITEMS
        global header_on_meta, header_on_json, first_call

        label = "parse_pages"
        global NOTHING_YIELDED
        NOTHING_YIELDED = False

        status_implies_removed = [404, 401]
        status_implies_pending_removal = [410]
        if response.status not in [200]:
            if response.status in status_implies_removed:
                with open(vv.REMOVED_FILE, 'a') as convert_file:
                    convert_file.write('\n' + response.url)
                return
            elif response.status in status_implies_pending_removal:
                print(f'This property is pending removal but will attempt scraping anyway! {response.url}')
            else:
                pass

        if SCRAPED_ITEMS > MAX_ITEMS:
            print(f"9 exceeded max scrape: ({SCRAPED_ITEMS} > {MAX_ITEMS})")
            return

        self.process_page(response)

    def process_page(self, response):

        global header_on_json, header_on_meta, SCRAPED_ITEMS

        stations = []
        all_codes2 = []
        all_links = []
        date_scraped_list = []

        all_links.append(response.url)

        info_block = {}

        hold_type = []
        short_description = []
        long_description = []
        special_attributes = response.css(pp.css_special_attributes).extract()

        if len(special_attributes) > 0:
            short_description.extend(special_attributes)

        selector = Selector(response)

        # All svg data-test, not really usable though
        # response.xpath('//svg[contains(@data-testid,"svg-")]').extract()
        # photo_text = response.xpath('//svg[@data-testid="svg-camera"]//following-sibling::span/text()').extract()

        photo_text = selector.xpath(pp.xpath_photo_text).extract()
        if len(photo_text) > 0:
            unique_photo_text = (list(set(photo_text)))
            short_description.append(pp.camera_stub + ";".join(unique_photo_text))

        virtual_tour_text = selector.xpath(pp.xpath_virtual_tour).extract()
        if len(virtual_tour_text) > 0:
            unique_virtual_tour_text = (list(set(virtual_tour_text)))
            short_description.append(pp.vt_stub + ";".join(unique_virtual_tour_text))

        floorplan_text = selector.xpath(pp.xpath_floorplan).extract()
        if len(floorplan_text) > 0:
            unique_floorplan_text = (list(set(floorplan_text)))
            short_description.append(pp.floor_stub + ";".join(unique_floorplan_text))

        inforeel_components = selector.xpath(pp.info_compnt)  # this one works, but would have to rework rest of code
        found_inforeel_item = False
        key, value = None, []
        for i in range(1):

            for child in inforeel_components:
                child_text = child.extract()
                # print('   ', child_text)

                if child_text.strip() == "":
                    pass
                elif child_text.upper() in ['PROPERTY TYPE', 'BEDROOMS', 'BATHROOMS', 'SIZE']:
                    key = child_text
                    found_inforeel_item = True
                    value = []
                elif child_text.upper() in ['Apartment'.upper(), 'Studio'.upper()]:
                    value.append(child_text)
                elif key and key not in ['BEDROOMS', 'BATHROOMS'] and len(child_text) > 2:
                    value.append(child_text)
                else:
                    mx = re.finditer(r'×(\d+)', child_text, re.I)

                    for match in mx:
                        # match.group()
                        value.append(match.group(1))
                        break

                info_block[key] = ";".join(value)

        if not found_inforeel_item:
            pass

        description_ui = selector.xpath(pp.xpath_description)
        for each in description_ui:
            each_text = " ".join(each.xpath('.//text()').extract())
            if len(each_text) < 1:
                pass
            elif len(each_text) < 3:
                pass
            elif len(each_text) < 30:
                if "hold" in each_text:
                    hold_type.append(each_text)
                else:
                    short_description.append(each_text)
            else:
                long_description.append(each_text)

        stations_panel = response.css(pp.css_stations)
        if False:
            station_distances = stations_panel.css(pp.css_station_text).extract()
            shortest_distance = 99999999
            for each_distance in station_distances:
                if "miles" in each_distance:
                    each_distance = float(each_distance.replace("miles", "").strip())
                    if each_distance < shortest_distance:
                        shortest_distance = each_distance

            stations.append(shortest_distance)

        else:
            shortest_distance = 99999999

            stats = []
            stat_name = []
            stat_distance = None
            train_types = []
            station_lines = stations_panel.xpath('.//li')
            for line in station_lines:

                line_divs = line.xpath('./div')
                for div in line_divs:
                    train_types.extend(div.xpath(pp.xpath_train_types).extract())

                line_spans = line.xpath('.//span')
                for span in line_spans:
                    span_texts = span.xpath('./text()').extract()

                    for span_text in span_texts:
                        if ' miles' in span_text:
                            stat_distance = float(span_text.replace("miles", "").strip())
                            if stat_distance < shortest_distance:
                                shortest_distance = stat_distance
                        else:
                            stat_name.append(span_text)
                stats.append((stat_distance, ";".join(stat_name), ";".join(train_types)))

                stat_name = []
                stat_distance = None
                train_types = []
            stations.append(shortest_distance)

        # crs_title = response.xpath('//h1[contains(@class,"title")]/text()')
        # crs_title_ext = crs_title.extract_first().strip()
        # ch_titles = response.css('h4.chapter__title::text')
        # ch_titles_ext = [t.strip() for t in ch_titles.extract()]
        # dc_dict[crs_title_ext] = ch_titles_ext

        valid_bullets = []
        bullet_points = selector.xpath('.//li')
        for each_bullet in bullet_points:
            bullet_extract = each_bullet.extract()
            # bullet_text = bullet_extract.xpath('./text()')
            if 'href' in bullet_extract or pp.seo in bullet_extract:
                pass
            else:
                valid_text_list = each_bullet.xpath('./text()').extract()
                valid_bullets.extend(valid_text_list)
        all_bullets = ";".join(valid_bullets)
        leftovers = info_block.copy()
        leftovers.pop("BEDROOMS", None)
        leftovers.pop("BATHROOMS", None)
        leftovers.pop("PROPERTY TYPE", None)
        leftovers.pop("SIZE", None)
        m = re.finditer(r'.*?/(\d+)', response.url, re.I)

        for match in m:
            # match.group()
            all_codes2.append(match.group(1))
            break

        # none of these need to be lists, we're adding a single item here
        data = {
            "ids": all_codes2,
            "version": ((vv.VERSION_LATEST + " ") * (len(all_codes2))).strip().split(" "),
            "link": all_links,
            "Station_Prox": stations,
            "type": [info_block.get('PROPERTY TYPE', None)],
            "bedrooms": [info_block.get('BEDROOMS', None)],
            "bathrooms": [info_block.get('BATHROOMS', None)],
            "size": [info_block.get('SIZE', None)],
            "other_key_info": [leftovers if bool(leftovers) else None],
            "bullet_points": [all_bullets],
            "station_info": [stats],
            "hold_type": hold_type,
            "short_description": ";;".join(short_description),
            "long_description": long_description,
            "date_scraped": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if not os.path.isfile(vv.LISTING_ENRICHED_FILE):
            df = pd.DataFrame.from_dict(data)
            df.set_index("ids", inplace=True)  # otherwise you get an anonymous first column
            # df.to_csv(vv.LISTING_ENRICHED_FILE, encoding="utf-8", header="true", index=False)
            self.write_to_csv__full(df, vv.LISTING_ENRICHED_FILE, [], vv.LISTING_ENRICHED_PUBLICATION)
        else:

            df_saved = pd.read_csv(vv.LISTING_ENRICHED_FILE)
            df_saved['ids'] = df_saved['ids'].astype('str')
            df_saved.set_index("ids", inplace=True)

            # with open('eggs.csv', 'a', newline='') as csvfile:
            with open(vv.LISTING_ENRICHED_FILE, 'a', newline='') as csvfile:
                if not all_codes2[0] in df_saved.index:
                    self.write_enriching_csv(all_codes2, all_links, info_block, stations, all_bullets, stats,
                                             hold_type,
                                             short_description, long_description, leftovers,
                                             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                elif (df_saved.loc[[all_codes2[0]]]["version"] < vv.VERSION_LATEST).all():
                    self.write_enriching_csv(all_codes2, all_links, info_block, stations, all_bullets, stats,
                                             hold_type,
                                             short_description, long_description, leftovers,
                                             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            # print('reached here 1/2')
            del df_saved

            potential_model_list = response.css('script::text').extract()
            for each in potential_model_list:
                if pp.MODEL in each:
                    page_model = each
                    break

            page_model_json = json.loads(page_model.strip().replace(pp.page_model_intro, ""))

            model_property = page_model_json[pp.model_property]
            model_meta = page_model_json[pp.model_meta]

            for each in pp.unneeded_model_array_1:
                model_property.pop(each, None)

            # Using a list comprehension to make a list of the keys to be deleted
            delete = [key for key in model_property if pp.unneeded_model_1 in key.lower()]
            # delete = [key for key in model_property if 'e' in key.lower()]
            # delete the key/s
            for key in delete:
                # print(key, "=", model_property[key])
                del model_property[key]

            for first_level in model_property.keys():
                # print("first_level:", first_level)
                if model_property[first_level] and type(model_property[first_level]) not in (bool, int):
                    delete = [key for key in model_property[first_level] if
                              ((type(key) == str) and (pp.unneeded_model_1 in key.lower()))]
                else:
                    # print("Level 1:", model_property[first_level], "is not a dictionary (or an empty dictionary)")
                    pass

                # delete = [key for key in model_property[first_level] if 'e' in key.lower()]
                for key in delete:
                    # print(key, "=", model_property[first_level][key])
                    if type(model_property[first_level]) == dict:
                        del model_property[first_level][key]
                    else:
                        print("something odd here")

            model_property["version"] = vv.VERSION_LATEST
            model_property["date_scraped"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(model_property)
            # df_property_app = pd.DataFrame.from_dict(model_property, orient='columns')
            df_property_app = pd.DataFrame.from_dict(pd.json_normalize(model_property), orient='columns')
            df_property_app.set_index("id", inplace=True)  # otherwise you get an anonymous first column

            if df_property_app[pp.dirty_text_1].str.find('<br')[0] > -1 or \
                    df_property_app[pp.dirty_text_1].str.find('\n')[0] > -1:
                df_property_app[pp.dirty_text_1] = df_property_app[pp.dirty_text_1].str.replace('<br />',
                                                                                                ';;;')
                converter = html2text.HTML2Text()
                converter.ignore_links = True
                handled = converter.handle(df_property_app[pp.dirty_text_1][0])
                # print(handled)  # Python 3 print syntax
                # df_property_app['text.description'][0] = handled.replace('\n','')
                df_property_app.loc[all_codes2[0], pp.dirty_text_1] = handled.replace('\n', ' ')

            if pp.special_property_1 in model_property["tags"]:
                # df_property_app.to_csv(vv.LISTING_JSON_MODEL_BID_FILE, mode='a', encoding="utf-8", index=True, header=True)
                try:
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_BID_TRIAL, mode='a', encoding="utf-8", index=True, header=False)
                    pd.read_csv(vv.LISTING_JSON_MODEL_BID_TRIAL)
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_BID_FILE, mode='a', encoding="utf-8", index=True, header=False)
                except:
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_BID_FAILED, mode='a', encoding="utf-8", index=True, header=False)
            else:
                # df_property_app.to_csv(vv.LISTING_JSON_MODEL_FILE, mode='a', encoding="utf-8", index=True, header=header_on_json)
                try:
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_TRIAL, mode='a', encoding="utf-8", index=True, header=False)
                    pd.read_csv(vv.LISTING_JSON_MODEL_TRIAL)
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_FILE, mode='a', encoding="utf-8", index=True, header=header_on_json)
                except:
                    df_property_app.to_csv(vv.LISTING_JSON_MODEL_FAILED, mode='a', encoding="utf-8", index=True, header=False)

            # df_original['bedrooms'] = df_original['Address'].str.extract('(bedroom)')
            # check if the csv file has been corrupted by <br> or other
            try:

                test = pd.read_csv(vv.LISTING_JSON_MODEL_FILE)
                test['id'].astype('int')
                header_on_json = False
                del test
            except:
                print(f"corrupted json model, at: {response.url}")
                pass

            model_meta["version"] = vv.VERSION_LATEST
            model_meta["date_scraped"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            model_meta["id_copy"] = model_meta['analyticsProperty']['propertyId']
            # print(model_meta)
            df_meta_appendable = pd.DataFrame.from_dict(pd.json_normalize(model_meta), orient='columns')
            df_meta_appendable.set_index("id_copy", inplace=True)  # otherwise you get an anonymous first column
            try:
                df_meta_appendable.to_csv(vv.LISTING_JSON_META_FILE, mode='a', encoding="utf-8", header=header_on_meta)
            except:
                print("******** there was some error writing the data! ********")
                print("******** there was some error writing the data! ********")
                print("******** there was some error writing the data! ********")

            # print('reached here 2/2')

            header_on_json = False
            header_on_meta = False

        SCRAPED_ITEMS += 1
        print(f"SCRAPED ITEMS: {SCRAPED_ITEMS} (SCRAPED LISTINGS: {SCRAPED_LISTINGS}) <-- {response.url}")

        # print(pd.DataFrame({k: sys.getsizeof(v) for (k, v) in locals().items()}, index=['Size']).T.sort_values(by='Size', ascending=False).head(4))

    def write_enriching_csv(self, all_codes2, all_links, info_block, stations, all_bullets, stats, hold_type,
                            short_description, long_description, leftovers, date_scraped):

        with open(vv.LISTING_ENRICHED_FILE, 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([
                all_codes2[0],
                vv.VERSION_LATEST.strip(),
                all_links[0],
                stations[0],
                info_block.get('PROPERTY TYPE', None),
                info_block.get('BEDROOMS', None),
                info_block.get('BATHROOMS', None),
                info_block.get('SIZE', None), leftovers if bool(leftovers) else None,
                all_bullets,
                stats,
                " ".join(hold_type),
                ";;".join(short_description),
                " ".join(long_description),
                date_scraped
            ])

    def sleep_long_or_short(self, long_sleep_chance=75, skip_sleep=False,
                            short_lowbound=2, short_highbound=7,
                            long_lowbound=15, long_highbound=70, source="--"):

        global multiplier

        if multiplier == 0:
            #print('N.B. sleep is disabled')
            return 0

        if NOTHING_YIELDED:
            sleep_time = random.randint(-1, 2)
        else:

            long_sleep_rand = random.randint(0, long_sleep_chance)
            long_sleep_time = random.randint(long_lowbound, long_highbound)
            short_sleep_time = random.randint(short_lowbound, short_highbound)
            if long_sleep_rand > long_sleep_chance - 1:
                print(f"{long_sleep_rand}/{long_sleep_chance}:, do a long wait ({long_sleep_time}) [from {source}]")
                sleep_time = long_sleep_time
            else:
                sleep_time = short_sleep_time
                print(f"sleep: {sleep_time} [from {source}] [multiplier is {multiplier} so actual sleep time is {sleep_time * multiplier}]")
            sleep_time = sleep_time * multiplier

        if sleep_time < 0: sleep_time = 0

        if not skip_sleep:
            time.sleep(sleep_time)
        else:
            return sleep_time


def debug_print(string):
    if DEBUG_ON:
        print(string)


# Initialize the dictionary **outside** of the Spider class
dc_dict = dict()

# Run the Spider
process = CrawlerProcess()

x = process.crawl(Splasher_spider)
y = process.start()
stations = []
all_codes2 = []
date_scraped = []

# pp.publish_dataframe(vv.LISTING_BASIC_FILE, droppable_basic, new_location=vv.LISTING_BASIC_PUBLICATION)
# pp.publish_dataframe(vv.LISTING_ENRICHED_FILE, droppable_enriched, drop_duplicates=True, new_location=vv.LISTING_ENRICHED_PUBLICATION)

print('reached the genuine end')
# quit()
# Print a preview of courses
# previewCourses(dc_dict)
