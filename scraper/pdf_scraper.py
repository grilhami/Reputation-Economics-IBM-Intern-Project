import logging
import urllib.request
import os
import re

from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader


ANNUAL_REPORT_YEAR = 2018
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

def pdf_scraper(url, cos, company, page_range, mode="both"):
    # Find the company name and page range of url
    company = company.replace(" ", "_")
    
    # Create path for original and parsed pdf
    pdf_path = f"assets/{company}/annual_report/"
    
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    
    print("Fetching document from URL...")

    headers={'User-Agent':USER_AGENT} 
    
    request=urllib.request.Request(url,None,headers)
    # Fetch data from url
    web_file = urllib.request.urlopen(request).read()
    print("Data fetched.")
    
    # Convert to stringio
    file_io = BytesIO(web_file)
    
    # Convert stringio to pdf reader
    pdf_file = PdfFileReader(file_io)
    
    pdf_writer = PdfFileWriter()
    
    bucket_name = "cos-standard-7ry"
    
    if mode == "parsed":
        # Parsed pdf file using page range
        for i in range(page_range[0], page_range[1]):
            pdf_writer.addPage(pdf_file.getPage(i))

        # Path for 
        filename = f"{company}_annual_report_{ANNUAL_REPORT_YEAR}_parsed.pdf"
        file_path = pdf_path + filename
        
        # Prepare byte
        writer_data = BytesIO()
        pdf_writer.write(writer_data)
        writer_data.seek(0)
        
        # Store to IBM COS
        cos.Object(bucket_name, file_path).put(Body=writer_data)
        
        return file_path
            
    if mode == "full":
        # Save pdf file based on path
        filename = f"{company}_annual_report_{ANNUAL_REPORT_YEAR}_full.pdf"
        file_path = pdf_path + filename
        
        cos.Object(bucket_name, file_path).put(Body=web_file)
        
        return file_path
            
    if mode == "both":
        
        # Parsed Version
        for i in range(page_range[0], page_range[1]):
            pdf_writer.addPage(pdf_file.getPage(i))

        filename = f"{company}_annual_report_{ANNUAL_REPORT_YEAR}_parsed.pdf"
        file_path_parsed = pdf_path + filename
        
        writer_data = BytesIO()
        pdf_writer.write(writer_data)
        writer_data.seek(0)
        
        cos.Object(bucket_name, file_path_parsed).put(Body=writer_data)
            
        # Full version
        filename = f"{company}_annual_report_{ANNUAL_REPORT_YEAR}_full.pdf"
        file_path_full = pdf_path + filename
        
        cos.Object(bucket_name, file_path_full).put(Body=web_file)
        
        return file_path_full, file_path_parsed
        