from jobDB import JobDB
import httpx
import datetime
from selectolax.parser import HTMLParser
import threading
import time
import random
import hashlib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

database = JobDB()

TOTAL_NUM_URLS = JobDB().get_num_documents()
BATCH_SIZE = 250

selectors = {
    "selenium-description": ["body > div.l-master > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone", "body > div > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone", "body > div.l-master > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone", "body > div.l-master > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone"],
    "regular-description": ["body > div > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone", "#k2-template > div > div.content"]
}

def get_description(selectors, parser):
    def try_get_description(selector):
        try:
            description = parser.css(selector)[0].text()
        except:
            return ""
        return description
    
    for selector in selectors:
        full_description = try_get_description(selector)
        if full_description != "":
            return full_description
    print("No description found")
    return "no description"


def crawl_pages(skip_to, NUM_URLS=100):
    job_db = JobDB()
    urls = job_db.get_items_to_update(skip=skip_to, num_urls=NUM_URLS)

    options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    with httpx.Client(base_url="https://www.karriere.at") as client:
        for data in urls:
            response = client.get(data[1])
            if response.status_code == 301 or response.status_code == 404:
                print(f"Job inactive {data[1]}")
                job_db.update_item(is_active=False, id=data[0], full_description=data[2], updated_at=datetime.datetime.now())
                continue

            elif response.status_code == 500:
                print(f"load with selenium {data[1]}")

                driver.get(data[1])
                html = driver.page_source
                parser = HTMLParser(html)
                full_description = get_description(selectors["selenium-description"], parser)
                job_db.update_item(is_active=True, id=data[0], full_description=full_description, updated_at=datetime.datetime.now())
                time.sleep(random.uniform(0.5, 1.5)) # trunk-ignore(bandit/B311)
                continue

            elif response.status_code != 200:
                print(f"Something wrong with request {response.status_code} {data[1]}")
                continue

            html = response.text
            parser = HTMLParser(html)
            full_description = get_description(selectors["regular-description"], parser)

            # encoder = hashlib.sha256()
            # encoder.update(full_description.encode("utf-8"))
            # encoded_description = encoder.hexdigest()
            # encoder.update(data[2].encode("utf-8"))
            # if encoded_description != encoder.hexdigest():
            #     print("Description changed since last crawl")
            #     # with open("description.txt", "w+") as file:
            #     #     file.write("NEW: "+full_description+"\n@@@@@@@\n OLD:" + data[2])
            #     time.sleep(10)

            job_db.update_item(is_active=True, id=data[0], full_description=full_description, updated_at=datetime.datetime.now())
            time.sleep(random.uniform(0.5, 1.5)) # trunk-ignore(bandit/B311)

        print(f"Thread {skip_to//BATCH_SIZE} done")
            

def main():
    num_threads = (TOTAL_NUM_URLS // BATCH_SIZE) + 1
    print(f"Launching {num_threads} threads")
    threads = []

    for thread_id in range(num_threads):
        thread = threading.Thread(target=crawl_pages, args=(thread_id*BATCH_SIZE,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()