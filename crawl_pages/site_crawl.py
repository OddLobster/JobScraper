import datetime
import hashlib
import json
import random
import time
from dataclasses import dataclass
import httpx
from selectolax.parser import HTMLParser
from jobDB import JobDB
import threading

lock = threading.Lock()
database = JobDB()

BATCH_SIZE = 50
NUM_PAGES = 500  # 500 max


@dataclass
class JobPosting:
    title: str
    company: str
    company_id: str
    salary: str
    company_url: str
    location: str
    country: str
    url: str
    description_snippet: str
    full_description: str
    employment_type: str
    posted_at: datetime.datetime
    is_active: bool
    last_active: datetime.datetime
    crawl_timestamp: datetime.datetime
    job_hash: str
    updated_at: datetime.datetime


def get_page(client, url, page):
    headers = {
        "cookie": "OptanonAlertBoxClosed=2023-01-30T23:14:28.474Z; FPID=FPID2.2.tXgT^%^2BnrFIMmeZBd^%^2Fc8x5FxFdECG^%^2FSF0r9XFyrlaxEcI^%^3D.1675120467; _hjSessionUser_411674=eyJpZCI6IjFjMzcxOGVmLTU5NmMtNTVmNS04YzA0LWUwYzk2MWMyZWZmZiIsImNyZWF0ZWQiOjE2NzUxMjA0NzkwMDQsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.1.1583817349.1675120467; _tt_enable_cookie=1; _ttp=DgyJMl7rUMBp9X05_aFbnkEfm6B; _fbp=fb.1.1690486421821.1711154956; _uetvid=de853060a0f311ed85f8930a0276a601; cto_bundle=iZy69F8wbXFnRzg3JTJCYkFFa2VFeWtEOVhONlhVTjZoQ1ZQZGlGa3A2VW11Uk0lMkIlMkZscm9JeGdMVm5hVmNieDlJdDBRdDZvT2NPbnNnYWhpVnF6VnNpc2JwMHRCNCUyQmN4amllS28lMkZLemNLcW9XeWx4MVhkeXFIMjMxZFVWS25iNDU1VENWYVglMkZwSURVenBwdEhFREQ4ZWRPM2VWN3clM0QlM0Q; _ga_VLJ9DMQTZG=GS1.1.1697459056.12.1.1697459095.0.0.0; oauth2_authenticated=karriere-sso-client; _gcl_au=1.1.1458778747.1700235814; PHPSESSID=t2u7dsqbmc592t5c5u7d058l86; KAC=e8a66651024d87ae4e589eb243a942080e167967db5bf872aad82365c5b67dc2; ReturningVisitor=true; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Nov+18+2023+18^%^3A43^%^3A15+GMT^%^2B0100+(Central+European+Standard+Time)&version=6.24.0&isIABGlobal=false&hosts=&consentId=cf95839f-c908-4a6b-87ff-0f1ef392deea&interactionCount=1&landingPath=NotLandingPage&groups=C0001^%^3A1^%^2CC0002^%^3A1^%^2CC0004^%^3A1&geolocation=AT^%^3B9&AwaitingReconsent=false; f0_uid=47c98ba3-dc1e-4e3a-9230-683d044818f2.1700329425389; f0_sid=408bf7af-9372-4e16-9ed3-1b682ab79be7.1700329425389.30; XSRF-TOKEN=eyJpdiI6IkNacEpmQlBnaStVUlJLYXd3Z3I3NXc9PSIsInZhbHVlIjoiellBZjVmS1Erc3pnOHFBNXlzdFVoZEE4bC9GK0lRbHVZd3VUcTNYTnd3TnNnU1BFaTJJaFZhS1I4V1pDVy81a1dSWVRDMnFucXk1YkVqTkxmcTlWRE13aHgwLzVWMnlIQ2dKNFgraGVlL1BHQXJGbDYyZ0JRYmorRVAvVTEzUk4iLCJtYWMiOiJmODA5ZTk3NjE1YjMxZGEyMmZiODA5MWFmNzEwYzc1YTgyOTY1Njc5N2IxNjFkNDhmMmMxYWFiNDJhMTBlZjcyIiwidGFnIjoiIn0^%^3D; laravel_session=eyJpdiI6InpJLzQzZTBHbFQ4cTlTUWIybjdQeFE9PSIsInZhbHVlIjoiS3hFRk9pWUJ5Zng2Y2IzMUdMVnN6NERrYXArOUNkWEkyY0lEbWNCVUxlU2Y4eHBVRERpMVYvWWpYOEhzVXErWTIybVhQYk1UY1p2RGcwRnRMSkh3VWUxQnROeWZoWE9ZbERKNG52SkRjY0J4Y3dud3hnYlZBUzkvZ1dvcTlTYjYiLCJtYWMiOiJhOGU3ZGEyNjY5Y2M2MDYyMDg1MGZlNWUzNzBkMzQ1NmI4N2QyZThmMTZmN2QzY2E5YjcyYTIzNGE5MTI2YTdjIiwidGFnIjoiIn0^%^3D",
        "authority": "www.karriere.at",
        "accept": "*/*",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "dnt": "1",
        "referer": "https://www.karriere.at/jobs",
        "sec-ch-ua": "^\^Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "^\^Windows^^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "x-csrf-token": "NYyyT1Wf4VtCiARJtJMDzJRToru83Uva1GfbgQ3W",
        "x-requested-with": "XMLHttpRequest",
    }
    
    try:
        response = client.get(url + page, headers=headers, timeout=30)
    except Exception as e:
        print("Connection probably timed out!\n", e)
        return -1
    
    if response.status_code != 200:
        print("Bad Response:", response.status_code)
        return -1
    
    html = response.text
    parser = HTMLParser(html)
    return parser


def process_job_list(job_list):
    job_temp = []
    for job in job_list:
        try:
            job = job["jobsItem"]
        except Exception:
            print("Not a job posting")
            continue
        encoder = hashlib.sha256()

        date = datetime.datetime.strptime(job["date"].replace("am ", ""), "%d.%m.%Y")
        encoder.update((job["title"] + job["snippet"] + job["locations"][0]["slug"] + str(date)).encode("utf-8"))
        item = JobPosting(
            title=job["title"],
            company=job["company"]["slug"],
            salary="-1",#job["salary"],
            company_url=job["company"]["link"],
            company_id=job["companyId"],
            location=job["locations"][0]["slug"],
            country="Austria",  #TODO currently hardcoded
            url=job["link"],
            description_snippet=job["snippet"],
            full_description="",
            employment_type="-1", #job["employmentTypes"],
            posted_at=date,
            is_active=True,
            last_active=datetime.datetime(1, 1, 1, 1, 1, 1),
            crawl_timestamp=datetime.datetime.now(),
            job_hash=encoder.hexdigest(),
            updated_at = datetime.datetime.now()
        )

        job_temp.append(item)
    return job_temp


def write_to_db(jobs):
    lock.acquire()
    database.insert_jobs(jobs)
    lock.release()

def crawl_pages(num_pages, url):
    with httpx.Client(base_url="https://www.karriere.at") as client:
        for page_nr in range(num_pages, num_pages + BATCH_SIZE):
            page = f"/jobs?page={page_nr}"
            page_data = get_page(client, url, page)
            if page_data == -1:
                print(f"Failed to load {page}")
                continue
            json_data = json.loads(page_data.text())

            job_list = json_data["data"]["jobsSearchList"]["activeItems"]["items"]
            jobs_from_page = process_job_list(job_list)

            write_to_db(jobs_from_page)

            time.sleep(random.uniform(0.5, 3.5))  # trunk-ignore(bandit/B311)
            print(f"Thread {num_pages//BATCH_SIZE} Crawled {page_nr - num_pages} pages")
        

def main():
    print("Starting site crawl")
    num_docs = database.get_num_documents()
    print(f"Total number of documents: {num_docs}")

    num_threads = (NUM_PAGES // BATCH_SIZE)
    print(f"Launching {num_threads} threads")
    threads = []

    url = "https://www.karriere.at"

    for thread_id in range(num_threads):
        thread = threading.Thread(target=crawl_pages, args=(thread_id*BATCH_SIZE, url))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    num_docs_after = database.get_num_documents()
    print(f"Number of documents added: {num_docs_after - num_docs}")

if __name__ == "__main__":
    main()

# rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com 
# rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com 
# rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com rapidapi.com 
