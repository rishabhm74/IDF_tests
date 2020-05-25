from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
import os
import urllib.request
import sqlite3

import random

from werkzeug.utils import secure_filename
import re
from Search import search_by_BM25

import pickle
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.stem import WordNetLemmatizer

from gensim.parsing.preprocessing import STOPWORDS

from spellchecker import SpellChecker
import random
from docx import Document
from auto_tagging_script import AutoTags

from final_script_fulldb import load_word_embeddings, cleaning_for_summarization, get_summary, writeTofile
from final_script_fulldb import PreProcess, valid_extensions
from main import *
from ready_for_search import *
def get_text_from_docx_document(file):
    try:
        doc = Document(file)
        temp = ''
        for para in doc.paragraphs:
            temp += para.text
        return temp
    except Exception:
        print('Raising......')
        raise Exception
def clean_query(query):
    '''
    Function to perform lemmatization and cleaning on query
    '''
    query = re.sub("'s", "", query)
    query = re.sub("s'", "", query)
    query = re.sub("n't", " not", query)
    lemmed = [WordNetLemmatizer().lemmatize(word) for word in word_tokenize(query) if word not in STOPWORDS]
    lemmed = [WordNetLemmatizer().lemmatize(word, pos='v') for word in lemmed]
    lemmed = list(set(lemmed))

    # applying spell checker on tags
    spell = SpellChecker()
    misspelled = spell.unknown(lemmed)
    new_query = query
    if len(misspelled) == 0:
        return lemmed, query, new_query
    else:
        correct_words = list(set(lemmed) - misspelled)
        correction = []

        for word in misspelled:
            # Get the one `most likely` answer
            correction.append(spell.correction(word))

        for i in range(len(correction)):
            new_query = new_query.replace(list(misspelled)[i], correction[i])


        # cleaned auto_tags
        lemmed = correct_words + correction
        print(f"Searching for {new_query} instead of {query}")
        return lemmed, query, new_query


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hard to guess string'


app.config['MAX_CONTENT_LENGTH	'] = 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'pptx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.before_first_request
def load_all_data():
    global data
    data = pickle.load(open(r"DataBase/data_file.pkl", "rb"))
    global titles
    titles = pickle.load(open(r"DataBase/title_file.pkl", "rb"))
    global auto_tag
    auto_tag = pickle.load(open(r"DataBase/svos_file.pkl", "rb"))
    global summary
    summary = pickle.load(open(r"DataBase/summary_file.pkl", "rb"))

    global data_for_tag 
    data_for_tag = pickle.load(open(r"DataBase/tags_pickle.pkl", "rb"))
    global data_for_text 
    data_for_text = pickle.load(open(r"DataBase/corpus_file.pkl", "rb"))
    global data_for_title 
    data_for_title = pickle.load(open(r"DataBase/title_corpus.pkl", "rb"))

    global document_file
    document_file = pickle.load(open(r"DataBase/document_file.pkl", "rb"))

    print("all data loaded...")





















@app.route('/')
def index():
    return render_template('index.html')


#changes start



@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':
        entered_text = request.form['search_bar']
        applied_filter_type = request.form['filter_type_name_holder']
        if applied_filter_type == "Search by Relevance":
            return redirect(url_for('viewSearchbyRelevance', the_text = entered_text))
        elif applied_filter_type == "Search by Tag":
            return redirect(url_for('viewSearchbyTag', the_text = entered_text))
        elif applied_filter_type == "Search by Title":
            return redirect(url_for('viewSearchbyTitle', the_text = entered_text))
            

    return redirect('/')
    #if request.method == 'POST':
     #   if applied_filter_type == "Search by Text":
      #      return redirect('/')
            #return applied_filter_type
        #elif applied_filter_type == "Search by Tag":
            #return applied_filter_type
        #elif applied_filter_type == "Search by Title":
            #return applied_filter_type



#changed end









@app.route('/searchByTag/<the_text>') #removed methods post get
def viewSearchbyTag(the_text):
    mystring = "Tag"
    query = the_text

    

    corpus = data_for_tag
    bm25 = search_by_BM25(corpus)

    tokenized_query, old_query, new_query = clean_query(query.lower())

    indexes, results = bm25.get_top_n(tokenized_query, data, n=5)
    results_titles = []
    results_summaries = []
    results_tags = []

    for i in indexes:
        results_titles.append(titles[i])
        results_summaries.append(summary[i])
        if auto_tag[i] != []:
            results_tags.append(list(set(random.choices(auto_tag[i], k=3))))
        else:
            results_tags.append(['No Auto tags'])
    text = []
    for i in results:
        text_to_show = " ".join(sent_tokenize(i)[:2])
        if text_to_show != '':
            text.append(text_to_show + '....')
        else:
            text.append(i)
    # text = results
    title = results_titles
    summaries = results_summaries
    tags = results_tags

    title_len = len(title)

    
    extension_list = []
    for i in indexes:
        extension_list.append(document_file[i]["extension"])


    return render_template('searchbyText.html', text=text, tag=query, title=title, summaries=summaries, tags=tags,
                            type=mystring ,title_len = title_len, old_query=old_query, new_query=new_query,extension_list=extension_list)



@app.route('/searchByRelevance/<the_text>')
def viewSearchbyRelevance(the_text):
    mystring = "Relevance"
    query = the_text

    corpus = data_for_text
    bm25 = search_by_BM25(corpus)

    tokenized_query, old_query, new_query = clean_query(query.lower())

    indexes, results = bm25.get_top_n(tokenized_query, data, n=5)
    results_titles = []
    results_summaries = []
    results_tags = []

    for i in indexes:
        results_titles.append(titles[i])
        results_summaries.append(summary[i])
        if auto_tag[i] != []:
            results_tags.append(list(set(random.choices(auto_tag[i], k=3))))
        else:
            results_tags.append(['No Auto tags'])
    text = []
    for i in results:
        text_to_show = " ".join(sent_tokenize(i)[:2])
        if text_to_show != '':
            text.append(text_to_show + '....')
        else:
            text.append(i)
    # text = results
    title = results_titles
    summaries = results_summaries
    tags = results_tags

    title_len = len(title)

    
    extension_list = []
    for i in indexes:
        extension_list.append(document_file[i]["extension"])

    # return render_template('searchbyText.html', text=text, tag=query, title=title, summaries=summaries, tags=tags, title_len = title_len)
    return render_template('searchbyText.html', text=text, tag=query, title=title, summaries=summaries, tags=tags,
                        type=mystring,title_len=title_len, old_query=old_query, new_query=new_query,extension_list=extension_list)


@app.route('/searchByTitle/<the_text>')
def viewSearchbyTitle(the_text):
    mystring = "Title"
    query = the_text


    corpus = data_for_title
    bm25 = search_by_BM25(corpus)

    tokenized_query, old_query, new_query = clean_query(query.lower())

    indexes, results = bm25.get_top_n(tokenized_query, data, n=5)
    results_titles = []
    results_summaries = []
    results_tags = []

    for i in indexes:
        results_titles.append(titles[i])
        results_summaries.append(summary[i])
        if auto_tag[i] != []:
            results_tags.append(list(set(random.choices(auto_tag[i], k=3))))
        else:
            results_tags.append(['No Auto tags'])
    text = []
    for i in results:
        text_to_show = " ".join(sent_tokenize(i)[:2])
        if text_to_show != '':
            text.append(text_to_show + '....')
        else:
            text.append(i)

    # text = results
    title = results_titles
    summaries = results_summaries
    tags = results_tags

    title_len = len(title)

    
    extension_list = []
    for i in indexes:
        extension_list.append(document_file[i]["extension"])

    # return render_template('searchbyTitle.html', text=text, tag=query, title=title, summaries=summaries, tags=tags, title_len = title_len)
    return render_template('searchbyText.html', text=text, tag=query, title=title, summaries=summaries, tags=tags,
                            type=mystring,title_len=title_len, old_query=old_query, new_query=new_query,extension_list=extension_list)


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(request.url)
        files = request.files.getlist(r'files[]')
        print(files[0].filename)
        file_upload = files[0].filename

        # taking filename as a title
        title = " ".join(file_upload.split('.')[:-1])

        try:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # go to that file and read it
            file_upload = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_upload)
            main(file_upload, title)
            # after completion of processsing delete that file from folder.
            os.remove(file_upload)

            # I know this way of doing it, is very wrong, It's more like a cheating. But I have done this for a particular reason
            # I will change it after sometime.

            return redirect('/')

        except Exception:
            print("Hello")
            return redirect('/')




var_path = ""
@app.route('/path', methods=['POST'])
def choose():
    app.config['UPLOAD_FOLDER'] = ""
    global var_path
    var_path = request.form.get('folder_path')

    print(var_path)
    app.config['UPLOAD_FOLDER'] = var_path
    #print(app.config['UPLOAD_FOLDER'])

    return redirect('/')
 

@app.route('/nopage')
def noaccountpagefunction():
    return render_template('nopage.html')


# tempdiv = ""
myclassname = ""


@app.route('/filenameonclick', methods=['GET', 'POST'])
def filenameonclick():
    if request.method == 'POST':
        if os.path.exists(var_path):

            myclassname = request.form['myclassname']
            print(myclassname)
            titles = pickle.load(open(r"DataBase/title_file.pkl", "rb"))
            for i in range(len(titles)):
                if titles[i] == myclassname:
                    index = i
                    break

            document_file = pickle.load(open(r"DataBase/document_file.pkl", "rb"))

            blob_data = document_file[index]["document"]
            extension = document_file[index]["extension"]

            if len(myclassname) > 80:
                myclassname = myclassname[:80]

            punctuations = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'
            for x in myclassname:
                if x in punctuations:
                    myclassname = myclassname.replace(x, "")

            print(myclassname)
            file_name = myclassname + '.' + extension
            file_name = os.path.join(var_path, file_name)

            writeTofile(blob_data, file_name)

            return render_template('redirect.html', myclassname=myclassname)
        else:
            mymessage = "Please enter the working directory for current session."
            return render_template('checkworking.html' , mymessage=mymessage)







@app.route('/acceptTitle', methods = ['GET', 'POST'])
def acceptTitle():
    theMainInput = request.form['mainInputVal']
    
    print(theMainInput)
    return jsonify({'returnData': theMainInput})




"""
@app.route('/theTest', methods = ['GET', 'POST'])
def theTest():
    theFinalTitle = request.form['theTitle']
    print("the value" + theFinalTitle)
    
    return jsonify({'theFinally' : theFinalTitle})
    #myList = [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
    #return jsonify({'theNumber' : myNum})
    #return jsonify({'theList' : myList})
"""


if __name__ == '__main__':
    app.run(debug=True)
