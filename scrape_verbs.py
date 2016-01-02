#!env/bin/python
# Python Standard Libraries
import csv
import re
# Third-Party Libraries
from lxml import html
import os
import requests
import unicodecsv as csv
import HTMLParser
# Custom Libraries
# N/A

htmlParser = HTMLParser.HTMLParser()


def generate_verb_forms():
    verb_row_output = []
    dictionary_form = "Iku"

    url = ("http"                               # protocol
           "://www.japaneseverbconjugator.com"  # hostname
           "/VerbDetails.asp"                   # path
           "?txtVerb=" + dictionary_form + ""   # query string
           "&Go=Conjugate")

    output_file_name = "output.csv"
    output_file_path = os.path.join(os.getcwd(), "output", output_file_name)

    webpage = requests.get(url)

    parser = html.HTMLParser(encoding='utf-8')
    tree_root = html.fromstring(webpage.content, parser=parser)

    # Gets the root table that all the information is in
    xpath = "/html/body/div[2]/div[1]/div[4]/div[1]/table[1]"

    selected_elements = tree_root.xpath(xpath)
    for selected_element in selected_elements:
        #----------------------------
        # Basic Verb Info Here
        #----------------------------
        class_element = selected_element.xpath("tr[1]/td")[0]
        verb_class = class_element.text.strip()
        verb_class_row = [u"" + dictionary_form + " Class", verb_class]

        stem_element = selected_element.xpath("tr[2]/td")[0]
        stem = stem_element.text.strip()
        stem_row = [u"" + dictionary_form + " Stem", stem]

        te_form_element = selected_element.xpath("tr[3]/td")[0]
        te_form = te_form_element.text.strip()
        te_row = [u"" + dictionary_form + " Te Form", te_form]

        infinitive_element = selected_element.xpath("tr[4]/td")[0]
        infinitive = infinitive_element.text.strip()
        infinitive_row = [u"" + dictionary_form + " Infinitive", infinitive]

        # Add rows to list
        # verb_row_output.append(verb_class_row)
        # verb_row_output.append(stem_row)
        # verb_row_output.append(te_row)
        # verb_row_output.append(infinitive_row)

        #----------------------------
        # Verb Form Info Here
        #----------------------------
        tbody = selected_element.xpath("tbody")[0]
        verb_form_rows = tbody.xpath("tr")

        # Removes top header row, it's trash and provides bad data
        verb_form_rows = verb_form_rows[1:]
        current_verb_form = None
        for verb_form_row in verb_form_rows:

            last_table_cell_index = len(verb_form_row)

            if last_table_cell_index == 4:
                current_verb_form_element = verb_form_row.xpath("td[1]")
                for t in current_verb_form_element:
                    element_markup = html.tostring(t)

                    verb_form_regex = re.compile("</button>[.\s]*(.*)[.\s]*</td>",
                                                 re.MULTILINE | re.IGNORECASE)
                    verb_forms = verb_form_regex.findall(element_markup)

                    current_verb_form = verb_forms[0]
                    current_verb_form = current_verb_form.strip()
                    current_verb_form = dictionary_form + " " + current_verb_form

                    #--------------
                    # Debugging
                    #--------------
                    # print current_verb_form
                    # print element_markup
                    # print verb_forms
                    # print t.tag
                    # print t.tail
                    # print t.text

            keigo_form_elements = verb_form_row.xpath(
                "td[" + str(last_table_cell_index - 2) + "]")[0]
            keigo_form = keigo_form_elements.text.strip(
            ) if keigo_form_elements.text else ""

            positive_form_elements = verb_form_row.xpath(
                "td[" + str(last_table_cell_index - 1) + "]")[0]
            positive_form = positive_form_elements.text.strip(
            ) if positive_form_elements.text else ""

            positive_kanji_elements = positive_form_elements.xpath(
                "span")
            positive_kanji = ""
            for positive_kanji_element in positive_kanji_elements:
                positive_kanji += positive_kanji_element.text

            negative_form_elements = verb_form_row.xpath(
                "td[" + str(last_table_cell_index) + "]")[0]
            negative_form = negative_form_elements.text.strip(
            ) if negative_form_elements.text else ""

            negative_kanji_elements = negative_form_elements.xpath(
                "span")
            negative_kanji = ""
            for negative_kanji_element in negative_kanji_elements:
                negative_kanji = negative_kanji_element.text

            positive_row_output = [
                positive_form,
                current_verb_form,
                positive_kanji,
                "Positive",
                keigo_form,
                dictionary_form,
            ]

            negative_row_output = [
                negative_form,
                current_verb_form,
                negative_kanji,
                "Negative",
                keigo_form,
                dictionary_form,
            ]
            #-----
            verb_row_output.append(positive_row_output)
            verb_row_output.append(negative_row_output)

        with open(output_file_path, "w") as csv_file_handle:
            verb_csv_writer = csv.writer(csv_file_handle)

            # verb_csv_writer.writerow([
            #     "Verb",
            #     "Verb Form",
            #     "Verb Tone",
            #     "Keigo Form",
            #     "Dictionary Form",
            # ])
            verb_csv_writer.writerows(verb_row_output)


def main():
    generate_verb_forms()

if __name__ == "__main__":
    main()
