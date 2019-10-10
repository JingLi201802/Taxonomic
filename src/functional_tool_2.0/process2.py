from flask import Flask, render_template, request, jsonify, redirect, make_response, url_for
from flask import send_file, send_from_directory, safe_join, abort
import xml.etree.ElementTree as ET
import os
from lxml import etree

import collections
import xlwt
import json

import PyPDF2
import requests
import pandas as pd
import re
#from nltk.corpus import words

from xlrd import open_workbook
from xlutils.copy import copy

import reference_info_extraction
import reference_new_stdds
import TaxonomyExtractPDF
import txtCrawl
import reader
import runTwoFunction

import zipfile 
from zipfile import ZipFile
import shutil

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'uploaded_folder'
app.config['CSV_FOLDER'] = 'csv_folder'

def zipzip(start_dir):
    start_dir = start_dir  
    file_news = start_dir + '.zip'  
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
        f_path = dir_path.replace(start_dir, '')  
        f_path = f_path and f_path + os.sep or ''  
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news


def write_excel(a_list, r_list,filename):
    book = xlwt.Workbook()
    sheet = book.add_sheet("agents", cell_overwrite_ok=True)
    reference_sheet = book.add_sheet("references", cell_overwrite_ok=True)
    
    cols = ["id", "type", "name", "familyName", "givenName", "members"]
    cols_ref = ["id", "type", "quickRef", "author", "author lookup", "year", "title"]
    title = sheet.row(0)
    title_ref = reference_sheet.row(0)
    for i in range(len(cols)):
        value = cols[i]
        title.write(i, value)
    for num in range(len(a_list)):
        row = sheet.row(num + 1)
        for index, col in enumerate(cols):
            if col in a_list[num].keys():
                value = a_list[num][col]
                row.write(index, value)
    for i in range(len(cols_ref)):
        value = cols_ref[i]
        title_ref.write(i,value)
    for num in range(len(r_list)):
        row = reference_sheet.row(num + 1)
        for index, col in enumerate(cols_ref):
            if col in r_list[num].keys():
                value = r_list[num][col]
                row.write(index, value)
    if not os.path.exists(app.config['CSV_FOLDER']):
        os.mkdir(app.config['CSV_FOLDER'])
    book.save(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls")

    agent_path = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("agents")
    # os.path.join(parent_dir, "csv_folder/{}_XmlOutput.csv".format("agents.csv"))
    references_path = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("references")
    # os.path.join(parent_dir, "csv_folder/{}_XmlOutput.csv".format("references.csv"))
    TNC_TaxonomicName_path = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_TaxonomicName")
    TNC_Taxonomic_name_usage = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_Taxonomic_name_usage")
    TNC_Typification = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_Typification")
    #Unknown = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format(filename.replace(".xml", ""))
    BibliographicResource = app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("BibliographicResource")
    """excel to csv """
    agents = pd.read_excel(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls", 'agents', index_col=0)
    agents.to_csv(agent_path, encoding='utf-8')
    references = pd.read_excel(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls", 'references', index_col=0)
    references.to_csv(references_path, encoding='utf-8')
    
    with ZipFile(app.config['CSV_FOLDER']+'/' + filename[:-4] +'.zip', 'w') as zipObj:
        # zipObj.write(agent_path,"agent.csv")
        # zipObj.write(references_path, "reference.csv")
        zipObj.write(TNC_TaxonomicName_path, "TNC_TaxonomicName.csv")
        zipObj.write(TNC_Taxonomic_name_usage, "TNC_Taxonomic_name_usage_XmlOutput.csv")
        zipObj.write(TNC_Typification, "TNC_Typification_XmlOutput.csv")
        #zipObj.write(Unknown,"{}_XmlOutput.csv".format(filename.replace(".xml", "")))
        zipObj.write(BibliographicResource,"BibliographicResource.csv")
    
    os.remove(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls")
    
    os.remove(TNC_TaxonomicName_path)
    os.remove(TNC_Taxonomic_name_usage)
    os.remove(TNC_Typification)
    os.remove(BibliographicResource)
    os.remove(agent_path)
    os.remove(references_path)
    #os.remove(TNC_TaxonomicName_path)



@app.route('/get/<filename>')
def uploaded_file(filename):
    print(filename)
    
    #return send_from_directory(app.config['CSV_FOLDER'], filename[:-3] + ".zip", as_attachment=True)
    return send_from_directory(app.config['CSV_FOLDER'], filename[:-3] + ".zip", as_attachment=True)

@app.route('/')
def index():
    return render_template('form.html')

@app.route("/", methods=["GET", "POST"])
def upload_file():
    agents_list = []
    reference_list = []
    file_tmp = ''
    if request.method == "POST":
        if request.files:
            if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
                os.mkdir(app.config['DOWNLOAD_FOLDER'])
            if not os.path.exists(app.config['CSV_FOLDER']):
                os.mkdir(app.config['CSV_FOLDER'])
            xml_file = request.files["xml"]
            if xml_file.filename.split('.')[-1] == 'xml':
                print("xml!")
                #xml_file = request.files["xml"]
                file_tmp = xml_file.filename
                xml_file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], xml_file.filename))
                print("file saved")
                #runTwoFunction.runall(app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename)
                #runTwoFunction.runall(xml_file.filename)
                
                
                path = app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename
                tree = ET.parse(path)
                root = tree.getroot()
                df = reader.get_info_from_body(root)
                df2 = reader.change_To_TNC_Taxonomic_name(df,path)
                # df2.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_TaxonomicName"))
                df3 = reader.mapping_to_TNC_Taxonomic_name_usage(df,df2,path)
                df4 = reader.mapping_to_typification(df, df2)
                
                #df2.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format(xml_file.filename.split(".")[0]))
                df2.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_TaxonomicName"))
                
                df3.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_Taxonomic_name_usage"))
                df4.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_Typification"))
                my_dict = reference_info_extraction.get_contri_info(app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename)
                reference_new_stdds.write_excel(my_dict,app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("BibliographicResource"))
                #my_dict[0][0].to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("BibliographicResource"))
                # reference_new_stdds.write_excel(my_dict)
                agents_list, reference_list = reference_info_extraction.get_contri_info(app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename)
                write_excel(agents_list, reference_list, xml_file.filename)
                #write_excel(my_dict)
            
            else:
                pdf_file = request.files["xml"]
                print("pdf!")
                pdf_tmp = pdf_file.filename
                file_tmp = pdf_tmp
                pdf_file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_file.filename))
                print("file saved")
                #TaxonomyExtractPDF.get_excel_output(app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename)
                TaxonomyExtractPDF.get_configurations()
                TaxonomyExtractPDF.pdf_to_text(app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename)
                txtCrawl.get_csv_output_test((app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename[:-4] +'.txt'), TaxonomyExtractPDF.direct_mappings, TaxonomyExtractPDF.get_output_path(pdf_file.filename[:-4]))
                zipzip(app.config['CSV_FOLDER'] + '/' + pdf_file.filename[:-4])

                os.remove(app.config['DOWNLOAD_FOLDER']+'/'+pdf_file.filename[:-4] +'.txt')
                shutil.rmtree(app.config['CSV_FOLDER']+'/'+pdf_file.filename[:-4])

    #return render_template('form.html')
    return render_template('form.html', agents=agents_list, reference=reference_list, xml_name=file_tmp)


if __name__ == '__main__':
    app.run(debug=True)
