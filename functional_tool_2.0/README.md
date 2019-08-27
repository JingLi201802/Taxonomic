This part temporarily does not involve the server, but only realizes the front-end and back-end data interaction through flask. Instructions are as follows:
1.    Git pull
2.    Open terminal, cd to this folder
3.    Enter “python3 process.py” to run
4.    Open a browser and copy the link after “Running on”, e.g. http://127.0.0.1:5000/
5.    Upload the XML/PDF file according to the prompts on the web page, and click "upload". Uploaded files will be automatically saved to a folder called "uploaded_folder"; output files -> .zip(If you upload an XML file) or .xls(If you upload an XML file) will be automatically saved to a folder called "csv_folder".
6.    The compressed package contains three files: 1. agents.csv; 2. reference.csv; 3. TNC_TaxonomicName.csv.
7.    If you upload an XML file, the page will display output
8.    Click "download" to download the output file to local
9.    Press CTRL+C to quit

