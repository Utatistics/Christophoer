import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class Crowler:
    def __init__(self, path_to_driver: str, target_url: str, path_to_output: str) -> None:
        self.path_to_driver = Service(path_to_driver)
        self.target_url = target_url
        self.path_to_output = path_to_output

        self.driver = webdriver.Chrome(service=self.path_to_driver)
        self.wait = WebDriverWait(self.driver, 30)

    def login(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        self.driver.get(self.target_url)
        self.driver.maximize_window()

        self.driver.find_element(By.CLASS_NAME,'nav__button-secondary').click()
        self.driver.find_element(By.ID, 'username').send_keys(self.username)
        self.driver.find_element(By.ID, 'password').send_keys(self.password)
        self.driver.find_element(By.CLASS_NAME, 'login__form_action_container ').click()
    
    def search_jobs(self, search_word: str) -> None:
        self.search_word = search_word
        print(f'searching the jobs: {self.search_word}')
  
        self.wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME,'search-global-typeahead__input')))
        self.driver.find_element(By.CLASS_NAME, 'search-global-typeahead__input').send_keys(self.search_word)
        self.driver.find_element(By.CLASS_NAME, 'search-global-typeahead__input').send_keys(Keys.ENTER)

        while True:
            cnt = 1
            self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH,f'//*[@id="main"]/div/div/div[{cnt}]/div[2]/a')))
            element = self.driver.find_element(By.XPATH, f'//*[@id="main"]/div/div/div[{cnt}]/div[2]/a')
            if 'job' in element.text:
                element.click()
                break 
            else:
                cnt += 1
                if cnt > 5:
                    print('Jobs not found.')
                    break
    
    def get_urls(self) -> None:
        self._implicitly_wait(3)
        self.urls = {}
        self.file_index = 0 
        
        page_cnt = 1
        while True:
            self.driver.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
            elements = self.driver.find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')
            num_of_elements = len(elements)
            print(f'{num_of_elements} elements found in page {page_cnt}.')

            elem_cnt = 0
            for element in elements:
                try:
                    self._url_getter(element)
                
                except NoSuchElementException:
                    self.driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth", block: "center"});', element)
                    self._implicitly_wait(1)
                    self._url_getter(element)

                elem_cnt += 1            
                eoe_stautus = self._iseoe(elem_cnt, num_of_elements)
                if eoe_stautus:
                    page_cnt += 1
                    pages = self.driver.find_element(By.CLASS_NAME, 'artdeco-pagination__pages').find_elements(By.TAG_NAME, 'li')
                    eop_status = self._page_turnner(page_cnt=page_cnt, elements=pages)
                    if eop_status:
                        print('All URls collected.')
                        break

            if eop_status:
                print(f'collected {len(self.urls)} jobs.')
                break

    def save_urls(self):
            dirname = self.path_to_output + self.search_word.replace(' ', '_')
            filename = dirname + '\\url_dict.json'
            with open(file=filename, mode='w') as fp:
                json.dump(self.urls, fp)

    def browse_job(self, load_opt: bool) -> None:
        self.job_html_dict = {}
        dirname = self.path_to_output + self.search_word.replace(' ', '_')
        os.system(f"mkdir {dirname}")

        if load_opt:
            with open(dirname + '\\url_dict.json') as fp:
                urls = json.load(fp)
        else:
            urls = self.urls

        for index in urls.keys():
            self.driver.get(urls[index])
            
            job_info_dict = self._job_info_getter()
            self._save_to_json(job_info_dict, index)

            title = self._job_text_getter(job_info_dict)
            self._save_to_txt(title, index)

    def _iseoe(self, elem_cnt: int, num_of_elements: int) -> bool:
        return elem_cnt == num_of_elements

    def _page_turnner(self, page_cnt: int, elements: WebElement) -> bool:
        iter_cnt = 0
        for page in elements:
            page_num = page.find_element(By.TAG_NAME, 'button').text        
            if page_num.isdigit(): page_num = int(page_num)
    
            if page_num == page_cnt:
                page.click()
                eop_status = False
                break

            elif page_num == '…' and iter_cnt > 1:
                page.click()
                eop_status = False
                break
               
            else:
                eop_status = True
            
            iter_cnt += 1
        
        print('page number: %s' % str(page_num))
        return eop_status  
    
    def _url_getter(self, element: WebElement) -> None:
        url = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
        self.urls[self.file_index] = url
        self.file_index += 1
        
    def _job_info_getter(self) -> dict:
        self._implicitly_wait(1)
        classname = {
            'title': 'jobs-unified-top-card__job-title',
            'company_name': 'jobs-unified-top-card__company-name',
            'location': 'jobs-unified-top-card__bullet',
            'posted_date': 'jobs-unified-top-card__posted-date',
            'applicants' : 'jobs-unified-top-card__applicant-count'}
        
        idname = {'salary': 'SALARY', 'location': 'Location'}      

        job_info_dict = {}
        for key in classname.keys():
            try:
                identifier = classname[key]
                src_get = f"element_{key} = self.driver.find_element(By.CLASS_NAME, '{identifier}')" 
                src_append = f"job_info_dict['{key}'] = element_{key}.text" 
                exec(src_get)
                exec(src_append)

            except NoSuchElementException:
                # print(f'{key} not found.')
                src_append = f"job_info_dict['{key}'] = None"
                exec(src_append)
        
        for key in idname.keys():
            try:
                identifier = idname[key]
                src_get = f"element_{key} = self.driver.find_element(By.ID, '{identifier}')"
                src_append = f"job_info_dict['{key}'] = element_{key}.text"
                exec(src_get)
                exec(src_append)
                    
            except NoSuchElementException:
                # print(f'{key} not found.')
                src_append = f"job_info_dict['{key}'] = None"
                exec(src_append)
        
        return job_info_dict
    
    def _job_icon_getter(self) -> None:
        self._implicitly_wait(1)
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, 'jobs-unified-top-card__job-insight')
        except NoSuchElementException:
            pass 
        self.data_icon_info = {}

    def _job_text_getter(self, job_info_dict: dict) -> str:
        self._implicitly_wait(1)
        try:
            text_data = self.driver.find_element(By.CLASS_NAME,'jobs-box__html-content').text
            title = job_info_dict['title'] + '_' +  job_info_dict['company_name']
            self.job_html_dict[title] = text_data
        except NoSuchElementException:
            title = None
        
        return title
    
    def _implicitly_wait(self, secs: int) -> None:
        time.sleep(secs)

    def _save_to_txt(self, title: str, index: int) -> None:
        print(f'writing to file_{index}.txt...')
        dirname = self.path_to_output + self.search_word.replace(' ', '_')
        filename = dirname + f'\\txt\\file_{index}.txt' 
        with open(file=filename, mode='w', encoding='utf-8') as f:
            if title:
                f.writelines(self.job_html_dict[title])
            else:
                print('page not found.')

    def _save_to_json(self, data: dict, index: int) -> None:
        print(f'writing to file_{index}.json...')
        dirname = self.path_to_output + self.search_word.replace(' ', '_')
        filename = dirname + f'\\json\\file_{index}.json'
        with open(file=filename, mode='w') as fp:
                json.dump(data, fp)
       
    def run(self, username: str, password: str, search_word: str, load_opt: bool) -> None:        
        self.load_opt = load_opt
        
        print('login...')
        self.login(username=username, password=password)
        self.search_jobs(search_word=search_word)

        if not self.load_opt:
            print('collecting the URLs...')
            self.get_urls()
            self.save_urls()

        print(f'browsing the job: place_holder')
        self.browse_job(load_opt=self.load_opt)
        
    def exit(self) -> None:
        time.sleep(3)
        self.driver.quit()

