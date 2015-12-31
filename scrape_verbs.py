#!env/bin/python
# Python Standard Libraries
import csv
# Third-Party Libraries
from lxml import html
import requests
# Custom Libraries
# N/A


def generate_verb_forms():
    url = ("http"                               # protocol
           "://www.japaneseverbconjugator.com"  # hostname
           "/VerbDetails.asp"                   # path
           "?txtVerb=iku&Go=Conjugate")         # query string
    output_file_name = "output.csv"
    webpage = requests.get(url)
    # print webpage
    # print webpage.content

    tree_root = html.fromstring(webpage.content)

    xpath = "/html/body/div[2]/div[1]/div[4]/div[1]/table[1]"
    # xpath =
    # "/html/body/div[2]/div[1]/div[4]/div[1]/table[1]/tbody[1]/tr[2]/td[3]"

    selected_elements = tree_root.xpath(xpath)
    # print selected_elements
    for selected_element in selected_elements:
        # print "Element: {}".format(selected_element)
        # print selected_element.text
        # print selected_element.xpath("//span[@class='JScript']")[0].text

        #----------------------------
        # Basic Verb Info Here
        #----------------------------
        class_element = selected_element.xpath("tr[1]/td")[0]
        stem_element = selected_element.xpath("tr[2]/td")[0]
        te_form_element = selected_element.xpath("tr[3]/td")[0]
        infinitive_element = selected_element.xpath("tr[4]/td")[0]

        verb_class = class_element.text.strip()
        stem = stem_element.text.strip()
        te_form = te_form_element.text.strip()
        infinitive = infinitive_element.text.strip()

        # print html.tostring(class_element)
        # print html.tostring(stem_element)
        # print html.tostring(te_form_element )
        # print html.tostring(infinitive_element)

        # print "Class: {}".format(verb_class)
        # print "Stem: {}".format(stem)
        # print "Te Form: {}".format(te_form)
        # print "Infinitive: {}".format(infinitive)

        #----------------------------
        # Verb Form Info Here
        #----------------------------
        tbody = selected_element.xpath("tbody")[0]
        verb_form_rows = tbody.xpath("tr")

        # print html.tostring(verb_form_rows)
        # print verb_form_rows.text

        # Removes top header row
        verb_form_rows = verb_form_rows[1:]
        for verb_form_row in verb_form_rows:

            last_table_cell_index = len(verb_form_row)

            keigo_form_element = verb_form_row.xpath(
                "td[" + str(last_table_cell_index - 2) + "]")[0]
            positive_form_element = verb_form_row.xpath(
                "td[" + str(last_table_cell_index - 1) + "]")[0]
            negative_form_element = verb_form_row.xpath(
                "td[" + str(last_table_cell_index) + "]")[0]

            keigo_form = keigo_form_element.text.strip(
            ) if positive_form_element.text else ""
            positive_form = positive_form_element.text.strip(
            ) if positive_form_element.text else ""
            negative_form = negative_form_element.text.strip(
            ) if negative_form_element.text else ""

            # print "Keigo form: {}".format(keigo_form)
            # print u"Positive: {} Negative: {}".format(positive_form,
            #                                           negative_form)


def main():
    generate_verb_forms()

if __name__ == "__main__":
    main()
