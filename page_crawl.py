from jobDB import JobDB
import httpx
import datetime
from selectolax.parser import HTMLParser
import threading
import time
import random
import hashlib

database = JobDB()

TOTAL_NUM_URLS = JobDB().get_num_documents()
BATCH_SIZE = 500

def crawl_pages(skip_to, NUM_URLS=100):
    job_db = JobDB()
    urls = job_db.get_items_to_update(skip=skip_to, num_urls=NUM_URLS)
    with httpx.Client(base_url="https://www.karriere.at") as client:
        for data in urls:
            response = client.get(data[1])
            if response.status_code != 200:
                print("Something wrong with request")
                continue
            html = response.text
            parser = HTMLParser(html)
            try:
                full_description = parser.css("body > div > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone")[0].text()
            except Exception:
                try:
                    full_description = parser.css("#k2-template > div > div.content")[0].text()
                except Exception as e:
                    print(f"{data[1]} needs special treatment or doesnt exist \n{e}")
                    print(f"Doesnt exist anymore {data[1]}")
                    with open("test.html", "w+") as file:
                        file.write(html)
                    job_db.update_item(is_active=False, id=data[0], full_description=data[2], updated_at=datetime.datetime.now())
                    continue
            finally:
                full_description = "no description"

            encoder = hashlib.sha256()
            encoder.update(full_description.encode("utf-8"))
            encoded_description = encoder.hexdigest()
            encoder.update(data[2].encode("utf-8"))
            if encoded_description != encoder.hexdigest():
                print("Description changed since last crawl")
                with open("description.txt", "w+") as file:
                    file.write("NEW: "+full_description+"\n@@@@@@@\n OLD:" + data[2])
                time.sleep(10)

            job_db.update_item(is_active=True, id=data[0], full_description=full_description, updated_at=datetime.datetime.now())
            time.sleep(random.uniform(0.5, 1.5)) # trunk-ignore(bandit/B311)
        print(f"Thread {skip_to//BATCH_SIZE} done")


num_threads = (TOTAL_NUM_URLS // BATCH_SIZE) + 1
print(f"Launching {num_threads} threads")
threads = []

for thread_id in range(num_threads):
    thread = threading.Thread(target=crawl_pages, args=(thread_id*BATCH_SIZE,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()