import logging
import urllib.request
import io
import os
import requests as r
import re
import subprocess
import tempfile

from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader


ANNUAL_REPORT_YEAR = 2018
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

def pdf_scraper(cos, url, company, page_range, mode="both"):
    # Find the company name and page range of url
    company = company.replace(" ", "_")
    url = url.replace(" ", "")
    
    # Create path for original and parsed pdf
    pdf_path = f"assets/{company}/annual_report/"
    
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    
    print("Fetching document from URL...")

    headers={'User-Agent':USER_AGENT} 

    # Fetch data from url
    try:
        request = r.get(url, headers=headers)
    except:
        request = r.get(url, headers=headers, verify=False)

    web_file = request.content
    print("Data fetched.")
    
    # Convert to stringio
    file_io = BytesIO(web_file)
    
    # Convert stringio to pdf reader
    pdf_file = PdfFileReader(file_io)
    if pdf_file.isEncrypted:
        try:
            pdf_file.decrypt("")
        except NotImplementedError:
            # Decrypt the PDF with qpdf

            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(web_file)
            temp_file_name = temp_file.name
            temp_file.close()

            decrypted_filename = f"{temp_file_name}.decrypted"

            # Need to install 'qpdf'
            command = f"qpdf --password= --decrypt {temp_file_name} {decrypted_filename}"

            try:
                status = subprocess.check_call(
                    command, shell=True, cwd="/tmp", timeout=300
                )

                with open(decrypted_filename, "rb") as f:
                    decrypted_document_data = f.read()

                pdf_file = PdfFileReader(
                    io.BytesIO(decrypted_document_data)
                )

            finally:
                os.unlink(temp_file_name)
                try:
                    # decrypted_filename may or may not have been created
                    os.unlink(decrypted_filename)
                except FileNotFoundError:
                    pass
    
    pdf_writer = PdfFileWriter()
    
    bucket_name = "cloud-object-storage-zg-cos-standard-275"
    
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
        