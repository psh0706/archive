from flask import Flask
from flask import send_file
from flask import jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import pandas as pd

app = Flask(__name__)
api = Api(app)

default_path = os.getcwd()

# kind1 = emotion,positive,negative,bigram
# kind2 = restaurant,tour,hotel

@app.route('/<kind1>/<kind2>/<country>/<title>', methods=['POST', 'GET'])
def return_img(kind1,kind2,country,title):
    try:
        filename =  default_path + '\\' + kind1 + '\\' + kind2 + '\\' + country + '\\' + title + '.png'
        print(filename)
        return send_file(filename, mimetype='image/gif')
    except Exception as ex:
        print(ex)

@app.route('/top/<kind>/<country>/<city>/<title>/<n>')
def top_tfidf(kind, country, city, title, n):
    
    with open(default_path+'\\TF-IDF\\'+kind+'\\'+country+'\\'+city+'.txt', 'rb') as f:
        X = pickle.load(f)
    
    cosine_df = pd.DataFrame((np.matrix(X.values) * np.matrix(X.values.T)).A, columns = list(X.index), index = list(X.index))

    Top = pd.DataFrame(cosine_df[title]).sort_values(title, ascending = False)[1:2]
    Top.index[0]
   
    Top_dict = {Top.index[0] : X.loc[Top.index[0]].sort_values(ascending = False)[0:int(n)].to_dict()}

    return jsonify(Top_dict)

@app.route('/rank/<kind>/<country>/<city>/<title>', methods=['POST', 'GET'])
def rank(kind,country,city,title):
    
    with open(default_path + '\\tf-idf\\'+country+'\\'+city+'.txt', 'rb') as f:
        X = pickle.load(f)
    
    cosine_df = pd.DataFrame((np.matrix(X.values) * np.matrix(X.values.T)).A, columns = list(X.index), index = list(X.index))

    rank = pd.DataFrame(cosine_df[title]).sort_values(title, ascending = False)[1:11]
    rank.rename({str(title) : 'Cosine Smilarity'}, axis = 'columns', inplace = True)
    rank['rank'] = list(range(1,11))    
    column_list = ['rank', 'Cosine Smilarity']
    rank = rank[column_list]
    
    return jsonify(rank.to_dict())

@app.route('/classification/<kind>/<country>/<city>/<text>')
def classification(kind, country, city, text):  

    with open(default_path+'\\Classification\\'+kind+'\\'+country+'\\'+city+'.txt', 'rb') as f:
        svm = pickle.load(f)

    return jsonify({'recommendation' : svm.predict([str(text)])[0]})

if __name__ == '__main__':
    def tokenizer_noun_adj(content):
        return content
    app.run(debug=True, host='0.0.0.0', port='7000')