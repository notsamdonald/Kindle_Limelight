import requests
import json
import pickle
import sys


DIR = 'F:\documents\My Clippings.txt'

# https://realpython.com/instance-class-and-static-methods-demystified/

class Highlights:
    def __init__(self, raw_string, id=0):
        self.raw_string = raw_string
        self.book_title = None
        self.book_author = None
        self.highlight = None
        self.highlight_type = None
        self.location = None
        self.date = None
        self.definition = None
        self.example = None
        self.valid_word = None

        offset = 1 if id == 0 else 0
        self.lines = raw_string.split('\n')[1+offset:-1]  # Discarding the quotation marks from text file

        self.valid = True if len(self.lines) == 4 else False
        if self.valid:
            # Continue with data processing if valid number of data points identified to minimize junk
            self.raw_book_string = self.lines[0]
            self.raw_highlight_info = self.lines[1]
            self.raw_highlight = self.lines[3]
            self.process_raw_book_string(self.raw_book_string)
            self.process_raw_highlighted_info(self.raw_highlight_info)
            self.process_raw_highlight(self.raw_highlight)

    def process_raw_book_string(self, raw_book_string):
        self.book_author = self.find_between(string=raw_book_string, start="(", end=")")
        self.book_title = self.find_between(string=raw_book_string, start=0, end="(")

        split_names = self.book_author.split(',')
        if len(split_names) > 1:
            self.book_author = split_names[-1] + " " + split_names[0]


    def process_raw_highlighted_info(self, raw_highlight_info):
        self.location = self.find_between(string=raw_highlight_info, start="Your Highlight at location ", end="|")
        self.date = self.find_between(string=raw_highlight_info, start="Added on ", end=-1)

    def process_raw_highlight(self, raw_highlight):
        self.highlight = raw_highlight

        highlight_length = len(self.highlight.split(" "))
        if highlight_length > 1:
            self.highlight_type = "Quote"
        else:
            self.highlight_type = "Word"
            self.process_word()

    def process_word(self):
        strip_chars = ['.', ',', ':', ';', ' ']  # Chars to be removed from single words (to ease definition lookup)
        for character in strip_chars:
            self.highlight = self.highlight.replace(character, '')
        self.highlight = self.highlight.capitalize()
        print(self.highlight)
        self.oxford_dictionary(self.highlight)

    def oxford_dictionary(self, word):
        # TODO: replace with your own app_id and app_key
        app_id = 'f582f0d3'
        app_key = '95d6c3e2906f718ac192d3c7cc6b6c83'
        language = 'en'
        word_id = word
        url = 'https://od-api.oxforddictionaries.com/api/v2/entries/' + language + '/' + word_id.lower()
        # url Normalized frequency
        urlFR = 'https://od-api.oxforddictionaries.com/api/v2/stats/frequency/word/' + language + '/?corpus=nmc&lemma=' + word_id.lower()
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        # print("code {}\n".format(r.status_code))
        # print("text \n" + r.text)
        # print("json \n" + json.dumps(r.json()))
        if r.status_code == 404:
            self.valid_word = False
        else:
            self.valid_word = True
            try:
                self.definition = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
                self.example = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['examples'][0]['text']
            except:
                self.valid_word = False

    @staticmethod
    def find_between(string, start, end):
        if end == -1:
            return string[string.find("{}".format(start)) + len(start):-1]
        elif start == 0:
            return string[0:string.find("{}".format(end))]
        else:
            return string[string.find("{}".format(start)) + len(start):string.find("{}".format(end))]


class NoteBook:
    def __init__(self, data):
        self.data = data

    def update(self, new_data):
        self.data.extend(new_data)

def main():

    f = open(DIR, "r", encoding="utf8")
    if f.mode == 'r':
        contents = f.read()

        higlight_list = []
        raw_text = contents.split('==========')

        for i, highlight_string in enumerate(raw_text):
            higlight_list.append(Highlights(highlight_string, i))

        for highlight in higlight_list:
            if highlight.valid and highlight.highlight_type == 'Word' and highlight.valid_word:
                print("Book:{}\nAuthor:{}\nHighlight:{}\nDefinition:{}\nExample:{}\n".format(highlight.book_title,
                                                                               highlight.book_author,
                                                                               highlight.highlight,
                                                                               highlight.definition,
                                                                               highlight.example))

        notebookObj = NoteBook(higlight_list)
        pickle.dump(notebookObj, open("notebook.p", "wb"))
        print('Complete')

    else:
        print('Failed to read')

def read_pickle():

    content = "This is Limelight, a bot designed to help Sam learn some words! Here are his 5 random daily words previously highlighted.\n\n"
    content += "Reply to this email describing any bugs observed :) and reply STOP to unsubscribe.\n"
    content += "https://github.com/Donald247/Kindle_Limelight\n"
    content += '---------------------------------------------------------------------------------------------\n\n'
    data = pickle.load(open("notebook.p", "rb" ))
    definition_list = []
    for highlight in data.data:
        if highlight.valid_word and highlight.valid and highlight.highlight_type == "Word":
            definition_list.append(highlight)
    import random

    definition_num = 5
    ids = random.sample(range(1, len(definition_list)), definition_num)
    print(ids)

    # Maunual overwrite for some nice definitions to test
    ids = [9, 37, 32, 1, 34]
    selected = list(definition_list[i] for i in ids)
    for defintion in selected:
        content = content + ("Book: {}\nAuthor: {}\nHighlight: {}\nDefinition: {}\nExample: {}\n\n".format(defintion.book_title,
                                                                                              defintion.book_author,
                                                                                              defintion.highlight,
                                                                                              defintion.definition,
                                                                                              defintion.example))

    content = content.encode('ascii', 'ignore').decode('ascii')
    send_email(content)

    print('wait')


def send_email(content):
    import smtplib, ssl

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "kindlelimelight@gmail.com"  # Enter your address
    password = 'limelight23'
    receiver_email = ["sdonald.uc@gmail.com","sdonald.uc@gmail.com"]  # Enter receiver address
    message = 'Subject: {}\n\n{}'.format('Daily Limelight Definitions!', content)

    context = ssl.create_default_context()


    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        for email in receiver_email:
            server.sendmail(sender_email, email, message)

read_pickle()
#main()

