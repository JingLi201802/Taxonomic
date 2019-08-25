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
from nltk.corpus import words

from xlrd import open_workbook
from xlutils.copy import copy

import reference_info_extraction
import TaxonomyExtractPDF
import reader
import runTwoFunction

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
	#book.save(app.config['CSV_FOLDER']+'/'+filename.rsplit('.',1)[0]+".xls")


@app.route('/get/<filename>')
def uploaded_file(filename):
    #print(filename)
    return send_from_directory(app.config['CSV_FOLDER'], filename.rsplit('.', 1)[0] + ".csv", as_attachment=True)


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
                runTwoFunction.runall(xml_file.filename)
                agents_list, reference_list = reference_info_extraction.get_contri_info(app.config['DOWNLOAD_FOLDER'] + '/' + xml_file.filename)
                write_excel(agents_list, reference_list, xml_file.filename)

        
            else:
                pdf_file = request.files["xml"]
                pdf_tmp = pdf_file.filename
                file_tmp = pdf_tmp
                pdf_file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_file.filename))
                print("file saved")
                TaxonomyExtractPDF.get_excel_output(app.config['DOWNLOAD_FOLDER'] + '/' + pdf_file.filename)

                #return render_template('form.html')

    return render_template('form.html', agents=agents_list, reference=reference_list, xml_name=file_tmp)


if __name__ == '__main__':
    app.run(debug=True)
