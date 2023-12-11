from jobDB import JobDB
import httpx
import datetime
from selectolax.parser import HTMLParser

job_db = JobDB()
urls = job_db.get_items_to_update(num_urls=100)
with httpx.Client(base_url="https://www.karriere.at") as client:
    for data in urls:
        print(data[1])
        response = client.get(data[1])
        html = response.text
        parser = HTMLParser(html)
        
        if parser.css("body > div.l-master > div.l-master__content > div > div > div.c-errorShow__info > h1"):
            print("Doesnt exist anymore")
            with open("test.html", "w+") as file:
                file.write(html)
            job_db.update_item(is_active=False, id=data[0], full_description=data[2], updated_at=datetime.datetime.now())
            continue

        full_description = parser.css("body > div > div.l-master__content > div > div > div > div.m-jobContent > div.m-jobContent__jobDetail > div.m-jobContent__jobText.m-jobContent__jobText--standalone")[0].text()
        job_db.update_item(is_active=True, id=data[0], full_description=full_description, updated_at=datetime.datetime.now())

