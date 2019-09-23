from flask import Flask, render_template, request, jsonify, redirect, make_response
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
#from nltk.corpus import words

from xlrd import open_workbook
from xlutils.copy import copy

import reference_info_extraction
import TaxonomyExtractPDF
import TaxonomyExtractPDF_2
import reader
import runTwoFunction


from zipfile import ZipFile

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'uploaded_folder'
app.config['CSV_FOLDER'] = 'csv_folder'


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

	"""excel to csv """
	agents = pd.read_excel(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls", 'agents', index_col=0)
	agents.to_csv(agent_path, encoding='utf-8')
	references = pd.read_excel(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls", 'references', index_col=0)
	references.to_csv(references_path, encoding='utf-8')

	with ZipFile(app.config['CSV_FOLDER']+'/' + filename[:-4] +'.zip', 'w') as zipObj:
		zipObj.write(agent_path,"agent.csv")
		zipObj.write(references_path, "reference.csv")
		zipObj.write(TNC_TaxonomicName_path, "TNC_TaxonomicName.csv")

	os.remove(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls")
	os.remove(agent_path)
	os.remove(references_path)
	os.remove(TNC_TaxonomicName_path)



@app.route('/get/<filename>')
def uploaded_file(filename):
    print(filename)

    #return send_from_directory(app.config['CSV_FOLDER'], filename[:-3] + ".zip", as_attachment=True)
    return send_from_directory(app.config['CSV_FOLDER'], filename[:-3] + ".zip", as_attachment=True)

# @app.route('/')
# def index():
#     return render_template('form.html')

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
                df2 = reader.change_To_TNC_Taxonomic_name(df)
                df2.to_csv(app.config['CSV_FOLDER']+'/'+"{}_XmlOutput.csv".format("TNC_TaxonomicName"))

                agents_list, reference_list = reference_info_extraction.get_contri_info(app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename)
                write_excel(agents_list, reference_list, xml_file.filename)


        
            else:
                pdf_file = request.files["xml"]
                print("pdf!")
                pdf_tmp = pdf_file.filename
                file_tmp = pdf_tmp
                pdf_file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_file.filename))
                print("file saved")
                TaxonomyExtractPDF.get_excel_output(app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename)

                # path = app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename
                # reader = TaxonomyExtractPDF_2.create_pdf_reader(path)
                # json = TaxonomyExtractPDF_2.parse_json_list(TaxonomyExtractPDF_2.find_new_names(TaxonomyExtractPDF_2.read_all_pages(reader)))
                # df = TaxonomyExtractPDF_2.add_dict_data_to_df(json)
                # df.fillna(0.0).to_csv(app.config['CSV_FOLDER']+'/'+ pdf_file.filename + ".csv")

                #return render_template('form.html')

    return render_template('form.html', agents=agents_list, reference=reference_list, xml_name=file_tmp)


if __name__ == '__main__':
    app.run(debug=True)
