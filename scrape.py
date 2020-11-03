from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from tasks import scrape_data
import uuid
import csv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

class FltaScraper():
    def __init__(self):
        self.file_name = self.create_file()
        opts = Options()
        opts.headless = True
        profile = webdriver.FirefoxProfile()

        profile.set_preference("dom.webnotifications.enabled", False)
        self.browser = webdriver.Firefox(firefox_profile=profile, options=opts, executable_path=f'{BASE_DIR}/geckodriver')
        self.flta_list()
        self.browser.close()


    def flta_list(self):
        self.browser.get('https://www.flta.org/IndMemberDirectory?&tab=1')
        time.sleep(2)
        count_urls = 0
        pages = self.browser.find_element_by_id('idPagingData')
        for i in range(len(pages.find_elements_by_tag_name('option'))):
            pages.find_elements_by_tag_name('option')[i].click()
            time.sleep(2)
            table = self.browser.find_element_by_tag_name('tbody')
            td_tags = self.browser.find_elements_by_class_name('memberDirectoryColumn1')
            
            print('--- page {i} of', len(pages.find_elements_by_tag_name('option')))
            for i, td in enumerate(td_tags):
                count_urls += 1
                link = td.find_element_by_tag_name('a').get_attribute('href')
                res = scrape_data.delay(link, self.file_name)
                break
            break
        print(f'Totally {count_urls} urls crawled and sent to celery for processing. Have a good day :)')
    

    def create_file(self):
        filename = 'flta_'+uuid.uuid4().hex
        header = [
            'Membership Level','Organization','First Name','Last Name', 'Nick Name',
            'Email', 'Street Address', 'City', 'State', 'Zip Code', 'Phone', 'Office', 'Job Title'
        ]
        new_file = open(f'all_scraped_data/{filename}.csv', 'w')
        writer = csv.writer(new_file)
        writer.writerow(header)
        new_file.close()
        return filename


FltaScraper()



