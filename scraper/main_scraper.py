import argparse
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--path_to_excel", required=True, help="Path to the excel file that contains the company list.")

args = vars(ap.parse_args())

PATH = args['path_to_excel']

def run_scraper(path):
    
    path_extension = path.split(".")[-1]
    
    if path_extension != "xlsx":
        raise ValueError("expected file with xlsx extension, but found '{}' instead.".format(path_extension))

    try:
        company_df = pd.read_excel(path)
    except Exception as e:
        raise ValueError(e)

    if "company_name" not in company_df.columns:
        raise KeyError("column name 'comapny_name' is not found in excel file.")
    else:
        companies = company_df['company_name'].values.tolist()

    return companies

if __name__ == "__main__":

    companies = run_scraper(PATH)

    print(companies)



print(PATH)