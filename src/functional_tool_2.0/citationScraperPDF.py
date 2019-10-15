from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.common.exceptions
import os


def get_bib_results(doi):
    results = dict()
    results["success"] = "false"
    results["formatchanged"] = "false"
    results["doi"] = doi

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1024x1400")
    chrome_options.add_argument

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "normal"
    chrome_driver = os.path.join(os.getcwd(), "chromedriver")

    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps, executable_path=chrome_driver)
    # Local debug - to be removed
    # driver.get("C:\\Users\\User\\Desktop\\Journal search results - Cite This For Me.html")
    driver.get("http://www.citethisforme.com/au/referencing-generator/apa")


    driver.execute_script("""document.querySelectorAll('[data-title="Search for journal articles by Title, Author, DOI, or URL"]')[0].click();
                            document.getElementsByName("jrQry")[0].value= "{}";
                            document.getElementsByClassName("button button--s1
                             search-form__button")[0].click();""".replace("\n", "").format(doi))

    author_elements = driver.find_elements_by_css_selector("div[class='input-row double']")
    author_index = 1
    for row_element in author_elements:
        last_name = row_element.find_element_by_css_selector('input[id$=Surname]')
        if not last_name.get_attribute("value") == "":
            first_name = row_element.find_element_by_css_selector('input[id$=Forename]')
            results["author{}".format(author_index)] = \
                first_name.get_attribute("value") + " " + last_name.get_attribute("value")
        author_index += 1

    # Either all fields will be found or none of them will be found until citethisforme updates their structure
    try:
        year = driver.find_element_by_id("Year")
    except:
        return results

    # Later-
    # Check if year number exists in PDF when the year = current year (avoid situations where it is just chosen by
    # default by citethisforme).

    try:
        results["year"] = year.find_element_by_css_selector("option[selected='selected']").get_attribute("value")
        results["title"] = driver.find_element_by_id("Title").get_attribute("value")
        results["journal"] = driver.find_element_by_id("ContainerTitle").get_attribute("value")
        results["volume"] = driver.find_element_by_id("Volume").get_attribute("value")
        results["pages"] = driver.find_element_by_id("Pages").get_attribute("value")
        results["database"] = driver.find_element_by_id("AvailableVia").get_attribute("value")
        results["url"] = driver.find_element_by_id("Url").get_attribute("value")
        results["success"] = "true"
    except selenium.common.exceptions.NoSuchElementException:
        # If one of the later fields are not present but an earlier field is, html structure has probably been changed
        results["formatchanged"] = "true"
        return results
    return results

# Given a results dictionary, append all authors by iterating over the dictionary, searching for author[x]
# keys then appending their values
def concat_authors(results_dic):
    return None
