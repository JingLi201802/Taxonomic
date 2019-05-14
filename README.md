# Taxonomic
This branch is for the web-based interface for this project.
Include the frontend and backend


This document is for the project front end. This part is development based on the HTML, CSS and Python script for Django. This part able user to connect with server and analysis information from files. The page contain one form and one table. The form is able to user to upload them pdf files to server to analysis. The table will dynamically update from server by using python and contained the information from user’s pdf files. The table is built on schema which designed by client. In the table user also will able to modified the data. 



Server should get the information from front page by using name attribute in tags and update information to front page by using name attribute as well. 



For the button tags, the onclick attribute is empty, that should be linked to script in the further when the script is done by server part. 

### To run demo, downlaod the demo folder individually, and run the script. 
This part temporarily does not involve the server, but only realizes the front-end and back-end data interaction through flask. Instructions are as follows:
1.    Download current folder
2.    Open terminal, type cd and drag the folder
3.    Enter “python3 process.py” to run
4.    Open a browser and copy the link after “Running on”, e.g. http://127.0.0.1:5000/
5.    Upload the XML file according to the prompts on the web page, and click "upload". Uploaded files will be automatically saved to a folder called "uploaded_folder". E.g. AnewNigerianHunterSnailSpecies.xml
6.    The page will display output, and you can download the.xls output file, which will be saved in a folder called "xls_folder".
7.    Press CTRL+C to quit

The next plan is to combine it with the front-end web design.
