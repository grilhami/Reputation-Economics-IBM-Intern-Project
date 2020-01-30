# Reputation-Economics-IBM-Intern-Project

Using IBM Cloud services to analyze company's financial performance based on CXO personality and company's reputation.

## How to run scraper
- Create a virtual environment with python 3.6+ and installed the require dependencies listed in requirements.txt by running 
`pip install -r requirements.txt`. For conveniency, create the virtual environment should be created in the same directory level as the 
repository

- activate the firtual environment by running `source venv/bin/activate`. replace `venv` with the appropriate virtual environment name.

- `cd Reputation-Economics-IBM-Intern-Project`

- `cd scraper`

- run `export PYTHONPATH=/path/to/orm:$PYTHONPATH`. Replace `/path/to/orm` to the full path of the `orm` folder.

- in `main_scrapper.py`, change the index value of list of company names as required (line 87-89).

- run the command `python main_scraper.py --path_to_excel path/to/excel_file` inside the `scraper` folder. Replace `path/to/excel_file` 
with the actual path to the excel file. 

## Additional notes for Windows
- Open venv/lib/site-packages/selenium/webdriver/common/service.py and change the cmd path (in def start function) to your chromedriver.exe

## Additional Infor regarding the `translate_selenium.py` file

An issue was encountered with using Python's Google Translate API for translation. In order to overcome this, a file nameed 
`translate_selenium.py` was created to handle translation. 

However there some limitations:
- Some setups are required to be able to run the script. Please refer to https://github.com/huseinzol05/Malaya/tree/master/translator
- The setup provided is only available for Linux and MacOs device. A recommended work-around for Microsoft user is to use the linux sub-system provided by the operating system.
