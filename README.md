# Reputation Economics: IBM Indonesia Intern Project
Using IBM Cloud Services to analyze company's financial performance based on CXO personality and company's reputation.
Programmers: Gilang Ramadhan Ilhami, Nicholas Dwiarto Wirasbawa.

# Reputation Economics Outline
- Getting all the basic information data consisting of company name, CXO, annual report link, and president director's message page on the annual report.
- Getting all the financial data from the company annual report. Transform it into a CSV.
- 3 programs were needed: ORM, Inference, and Scraper.
- Utilizing the scraper to get all the basic information data.
- Using the ORM to put the gathered data into IBM DB2 on Cloud.
- Utilizing the scraper again to scrape president director messages and storing them in IBM COS.
- Using the ORM to get all the paths/data from the IBM DB2 on Cloud.
- Using Inference to gain an insight about the personality of each President Directors.
- The Inference program also pulls (if data is a path) and parses the data from IBM COS.
- Utilizing the Inference again to get an insight about corporate's reputation.
- Merge all of resulting CSV's into one CSV.
- Data analysis!

## How to Install
- Export or pull the repository.

- Create a virtual environment with Python 3.6+ and install the required dependencies listed in requirements.txt by running  `pip install -r requirements.txt`. For conveniency, the virtual environment should be created in the same directory level as the repository. Suggested virtual environment name is `.venv`.

- Activate the virtual environment by running:
Mac/Linux: `source venv/bin/activate`. 
Windows: `C:\path\to\venv\Scripts\activate.bat`
Replace `venv` with the appropriate virtual environment name.

## How to run Scraper
- Use `cd path-to-repo-folder`.

- Use `cd scraper`.

- Run: 
Mac/Linux: `export PYTHONPATH=/path/to/orm:$PYTHONPATH`. 
Windows: Change the system variable to include the path to `orm` folder.
Alternative: Copy the `orm.py` file into the same directory that you run your script (whether scraper or inference/insight).
Replace `/path/to/orm` to the full path of the `orm` folder.

- In `main_scrapper.py`, change the index value of list of company names as required (line 87-89).

- Run the command `python main_scraper.py --path_to_excel path/to/excel_file` inside the `scraper` folder. Replace `path/to/excel_file` with the actual path to the excel file. 

## How to run Inference - Personality Insight
- Download `chromedriver`.

- Open `venv/lib/site-packages/selenium/webdriver/common/service.py` and change the cmd path (in `def start` function)to your `chromedriver.exe` file. It should be located in `C:\Users\chromedriver.exe` so Windows knows exactly what the program was doing. Set the cmd to be = `[path-to-chromedriver]`.

- For Mac/Linux, simply run `sudo nano /etc/paths/` and edit the path from there.

- Run the test by using `python insight.py`. Make sure that you are in the inference folder.

- Make sure the code in `def main()` is uncommented for `personality_insight_processor` function!

## Additional Information regarding the `translate_selenium.py` file
An issue was encountered with using Python's Google Translate API for translation. In order to overcome this, a file named `translate_selenium.py` was created to handle translation. 

However, there are some limitations:
- Some setups are required to be able to run the script. Please refer to https://github.com/huseinzol05/Malaya/tree/master/translator
- The setup provided is only available for Linux and MacOs device. A recommended work-around for Microsoft user is to use the linux sub-system provided by the operating system.
