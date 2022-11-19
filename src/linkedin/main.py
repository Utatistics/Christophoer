import os 
from pathlib import Path
from linkedin.util.crowler import Crowler 
from linkedin.util.db import DbMaker 

path_to_driver = Path(os.getenv('PYPJ')) / 'Crowler/driver/chromedriver_win32/chromedriver.exe'
path_to_linkedin = 'https://linkedin.com'
username = 'frusciante2580@gmail.com'
password = 'Utatistics0511'
search_word = 'data scientist'
path_to_output = os.getcwd() + '\\..\\..\\output\\'

colnames = ['Python', 'SQL', 'C++','MSc', 'PhD', 'Cloud', 'AWS', 'Azure', 'Statistics','Statistical', 'Computer Science', 'CS'] 

def collect_data():
    clowler = Crowler(path_to_driver=path_to_driver, target_url=path_to_linkedin, path_to_output=path_to_output)
    clowler.run(username=username, password=password, search_word=search_word, load_opt=True)
    clowler.exit()

def make_db():
    dbmaker = DbMaker(path_to_output=path_to_output, search_word=search_word)
    dbmaker.run(colnames)

def main():
    # collect_data()
    make_db()
    
if __name__ == '__main__':
    print('Hello LinkedIn!')
    main()
    print('Goodbye.')
