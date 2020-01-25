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
