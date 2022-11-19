import os 
import csv
import json
import re
from re import Pattern

path_to_output = os.getcwd() + '\\..\\..\\output\\'
search_word = 'data scientist'

class DbMaker:
    def __init__(self, path_to_output: str, search_word: str) -> None:
        self.path_to_output = path_to_output + search_word.replace(' ', '_') + '\\'
        self.path_to_txt = path_to_output + search_word.replace(' ', '_') + '\\txt\\'
        self.path_to_json = path_to_output + search_word.replace(' ', '_') + '\\json\\'
        self.dbname = path_to_output + search_word.replace(' ', '_') + '\\database.csv'
        self.num_of_entries = len(os.listdir(self.path_to_txt))
        self.encoding = 'utf-8'
        self.newline = ""
    
    def create_csv(self, colnames: list) -> None:
        self.default_keys = ['filename', 'title','company_name', 'location','posted_date', 'applicants', 'salary']
        self.colnames = colnames
        self.header = [*self.default_keys, *self.colnames]
        self.header.append('Salary')

        with open(file=self.dbname, mode='w', encoding=self.encoding, newline=self.newline) as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
    
    def write_to_csv(self) -> None:
        with open(file=self.dbname, mode='a', encoding=self.encoding, newline=self.newline) as f:
            writer = csv.writer(f)

            for jsonfile in os.listdir(self.path_to_json):
                txtfile = jsonfile.replace('json','txt')
                row = self._write_job_info(jsonfile)
                row = self._write_job_contents(txtfile, row)
                writer.writerow(row)

    def _write_job_info(self, jsonfile: str) -> list:
        row = [jsonfile.replace('.json','')]
        with open(file=self.path_to_json + jsonfile, mode='r',encoding=self.encoding) as fp:
            job_info_dict = json.load(fp)
            for key in job_info_dict.keys():
                row.append(job_info_dict[key])
            return row
            
    def _write_job_contents(self, txtfile: str, row: list) -> list:
        with open(file=self.path_to_txt + txtfile, mode='r', encoding=self.encoding) as f:
            job_info_txt = f.readlines()
            compiled = re.compile('\D*\d\d,000\D*')

            for word in self.colnames:
                status = False
                row = self._get_bool_info(row, job_info_txt, status, word)
            
            row = self._get_saraly(row, job_info_txt, compiled)

        return row
    
    def _get_bool_info(self, row: list, job_info_txt: list, status: bool, word: str) -> list:
        for line in job_info_txt:
            if word in line:
                status = True
                break
        row.append(status)
        return row 

    def _get_saraly(self, row: list, job_info_txt: list, compiled: Pattern) -> list:
        for line in job_info_txt:
            matched  = compiled.match(line)
            try:
                salary = re.sub(r'\D', '', matched.group())
                row.append(salary)
                break
            except AttributeError:
                pass
        
        row.append(None)
        return row

    def run(self, colnames: list):
        self.create_csv(colnames)
        self.write_to_csv()
 