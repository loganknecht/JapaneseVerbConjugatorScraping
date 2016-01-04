#!env/bin/python
# Python Standard Libraries
import re
# import re
# Third-Party Libraries
from lxml import html
from lxml.html.clean import clean_html
import os
import requests
import unicodecsv as csv
import HTMLParser
# Custom Libraries
# N/A

htmlParser = HTMLParser.HTMLParser()


def generate_verb_list():
    verb_list_url = "http://www.japaneseverbconjugator.com/JVerbList.asp"
    verb_list_webpage = requests.get(verb_list_url)
    parser = html.HTMLParser(encoding='utf-8')
    verb_list_tree_root = html.fromstring(verb_list_webpage.content,
                                          parser=parser)
    verb_list_xpath = "/html/body/div[3]/div[1]/div[4]/div[1]/table"
    table_element = verb_list_tree_root.xpath(verb_list_xpath)[0]
    table_row_elements = table_element.xpath("tr")
    for table_row_element in table_row_elements:
        for verb_list in table_row_element.xpath("td"):
            print verb_list[0].text


def generate_verb_forms():
    os.makedirs("output_files")
    verb_row_output = []
    dictionary_form = "Iku"

    verb_form_url = ("http"                               # protocol
                     "://www.japaneseverbconjugator.com"  # hostname
                     "/VerbDetails.asp"                   # path
                     "?txtVerb=" + dictionary_form + ""   # query string
                     "&Go=Conjugate")

    verb_properties_filename = "{} {}.csv".format(dictionary_form,
                                                  "Verb Properties")
    verb_properties_filepath = os.path.join(os.getcwd(),
                                            "output_files",
                                            verb_properties_filename)

    verb_form_filename = "{} {}.csv".format(dictionary_form,
                                            "Verb Forms")
    verb_form_filepaths = os.path.join(os.getcwd(),
                                       "output_files",
                                       verb_form_filename)

    verb_form_webpage = requests.get(verb_form_url)

    parser = html.HTMLParser(encoding='utf-8')
    tree_root = html.fromstring(verb_form_webpage.content, parser=parser)

    # Gets the root table that all the information is in
    xpath = "/html/body/div[2]/div[1]/div[4]/div[1]/table[1]"

    selected_elements = tree_root.xpath(xpath)
    for selected_element in selected_elements:
        #----------------------------
        # Basic Verb Info Here
        #----------------------------
        class_element = selected_element.xpath("tr[1]/td")[0]
        class_kanji_element = class_element.xpath("span")[0]
        verb_class_kanji = class_kanji_element.text
        class_element_text = re.sub("~", "", class_element.text)
        verb_class_split = class_element_text.split()
        verb_class_split = [verb_class.strip()
                            for verb_class
                            in verb_class_split]

        verb_class = verb_class_split[0].strip()
        verb_class_column = "{} Class Level".format(dictionary_form)
        verb_class_row = [verb_class_column, verb_class, verb_class_kanji]

        dan_class = verb_class_split[1].strip()
        dan_class_column = "{} ~Dan Class".format(dictionary_form)
        dan_class_row = [dan_class_column, dan_class, verb_class_kanji]

        stem_column = "{} Stem".format(dictionary_form,
                                       "Stem")
        stem_element = selected_element.xpath("tr[2]/td")[0]
        stem_kanji_element = stem_element.xpath("span")[0]
        stem_kanji = stem_kanji_element.text
        stem = stem_element.text.strip()
        stem_row = [stem_column, stem, stem_kanji]

        te_form_column = "{} Te Form".format(dictionary_form)
        te_form_element = selected_element.xpath("tr[3]/td")[0]
        te_form_kanji_element = te_form_element.xpath("span")[0]
        te_form_kanji = te_form_kanji_element.text
        te_form = te_form_element.text.strip()
        te_row = [te_form_column, te_form, te_form_kanji]

        infinitive_column = "{} Infinitive".format(dictionary_form,
                                                   "Infinitive")
        infinitive_element = selected_element.xpath("tr[4]/td")[0]
        infinitive_kanji_element = infinitive_element.xpath("span")[0]
        infinitive_kanji = infinitive_kanji_element.text
        infinitive = infinitive_element.text.strip()
        infinitive_row = [infinitive_column, infinitive, infinitive_kanji]

        with open(verb_properties_filepath, "w") as csv_file_handle:
            verb_csv_writer = csv.writer(csv_file_handle)
            verb_csv_writer.writerow(verb_class_row)
            # verb_csv_writer.writerow(verb_class_kanji_row)
            verb_csv_writer.writerow(dan_class_row)
            verb_csv_writer.writerow(stem_row)
            # verb_csv_writer.writerow(stem_kanji_row)
            verb_csv_writer.writerow(te_row)
            # verb_csv_writer.writerow(te_form_kanji_row)
            verb_csv_writer.writerow(infinitive_row)
            # verb_csv_writer.writerow(infinitive_kanji_row)

        #-----------------------------------------------------------------------
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

            #-------------------------------------------------------------------
            # TODO: REFACTOR SO THAT THIS AND POSITIVE FORMS ARE A SINGLE
            # FUNCTION
            positive_form_elements = verb_form_row.xpath(
                "td[" + str(last_table_cell_index - 1) + "]")

            positive_forms = []
            positive_kanji_forms = []

            for positive_form_element in positive_form_elements:
                # print html.tostring(positive_form_element)
                spans = positive_form_element.xpath('span')
                for span in spans:
                    positive_form_element.remove(span)

                raw_html = html.tostring(positive_form_element)
                raw_html = clean_html(raw_html)
                raw_html = re.sub("<br>", "", raw_html)
                raw_html = re.sub("<td>", "", raw_html)
                raw_html = re.sub("</td>", "", raw_html)
                # print raw_html

                for line in raw_html.split("\n"):
                    positive_forms.append(line.strip())

                positive_forms = [positive_form
                                  for positive_form in positive_forms
                                  if positive_form]
                for span in spans:
                    positive_kanji_forms.append(span.text)

            if len(positive_forms) < len(positive_kanji_forms):
                # print "less english than kanji"
                while len(positive_forms) < len(positive_kanji_forms):
                    positive_forms = [""] + positive_forms
            elif len(positive_forms) > len(positive_kanji_forms):
                # print "less kanji than english"
                while len(positive_forms) > len(positive_kanji_forms):
                    positive_kanji_forms = [""] + positive_kanji_forms

            for positive_form, positive_kanji_form in zip(positive_forms, positive_kanji_forms):
                positive_row_output = [
                    positive_form,
                    current_verb_form,
                    positive_kanji_form,
                    "Positive",
                    keigo_form,
                    dictionary_form,
                ]
                verb_row_output.append(positive_row_output)
            #-------------------------------------------------------------------
            # TODO: REFACTOR SO THAT THIS AND POSITIVE FORMS ARE A SINGLE
            # FUNCTION
            negative_form_elements = verb_form_row.xpath(
                "td[" + str(last_table_cell_index) + "]")

            negative_forms = []
            negative_kanji_forms = []

            for negative_form_element in negative_form_elements:
                # print html.tostring(negative_form_element)
                spans = negative_form_element.xpath('span')
                for span in spans:
                    negative_form_element.remove(span)

                raw_html = html.tostring(negative_form_element)
                raw_html = clean_html(raw_html)
                raw_html = re.sub('<br>', '', raw_html)
                raw_html = re.sub('<td>', '', raw_html)
                raw_html = re.sub('</td>', '', raw_html)
                # print raw_html

                for line in raw_html.split("\n"):
                    negative_forms.append(line.strip())

                negative_forms = [negative_form
                                  for negative_form in negative_forms
                                  if negative_form]
                for span in spans:
                    negative_kanji_forms.append(span.text)

            if len(negative_forms) < len(negative_kanji_forms):
                # print "less english than kanji"
                while len(negative_forms) < len(negative_kanji_forms):
                    negative_forms = [""] + negative_forms
            elif len(negative_forms) > len(negative_kanji_forms):
                # print "less kanji than english"
                while len(negative_forms) > len(negative_kanji_forms):
                    negative_kanji_forms = [""] + negative_kanji_forms

            for negative_form, negative_kanji_form in zip(negative_forms, negative_kanji_forms):
                negative_row_output = [
                    negative_form,
                    current_verb_form,
                    negative_kanji_form,
                    "Negative",
                    keigo_form,
                    dictionary_form,
                ]
                verb_row_output.append(negative_row_output)
            #-------------------------------------------------------------------

        with open(verb_form_filepaths, "w") as csv_file_handle:
            verb_csv_writer = csv.writer(csv_file_handle)
            verb_csv_writer.writerows(verb_row_output)


def main():
    generate_verb_forms()

if __name__ == "__main__":
    main()
