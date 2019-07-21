from flask import Flask, render_template, request, redirect, url_for, jsonify
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import folium

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = int(request.form['city'])
        alcohol = int(request.form['alcohol'])
        smoking_area = int(request.form['smoking_area'])
        dress_code = int(request.form['dress_code'])
        price = int(request.form['price'])
        Rambience = int(request.form['Rambience'])
        area = int(request.form['area'])

        # 1) option for city
        if city == 0:
            city_Cuernavaca = 0; city_Jiutepec = 0; city_San_Luis_Potosi = 1; city_Soledad = 0
            city_str = 'San Luis Potosi'
        elif city == 1:
            city_Cuernavaca = 0; city_Jiutepec = 0; city_San_Luis_Potosi = 0; city_Soledad = 0
            city_str = 'Ciudad Victoria'
        elif city == 2:
            city_Cuernavaca = 1; city_Jiutepec = 0; city_San_Luis_Potosi = 0; city_Soledad = 0
            city_str = 'Cuernavaca'
        elif city == 3:
            city_Cuernavaca = 0; city_Jiutepec = 1; city_San_Luis_Potosi = 0; city_Soledad = 0
            city_str = 'Jiutepec'
        else:
            city_Cuernavaca = 0; city_Jiutepec = 0; city_San_Luis_Potosi = 0; city_Soledad = 1
            city_str = 'Soledad'

        # 2) option for alcohol
        if alcohol == 0:
            alcohol_No_Alcohol_Served = 1; alcohol_Wine_Beer = 0
            alcohol_str = 'No alcohol served'
        elif alcohol == 1:
            alcohol_No_Alcohol_Served = 0; alcohol_Wine_Beer = 1
            alcohol_str = 'Wine & Beer'
        else:
            alcohol_No_Alcohol_Served = 0; alcohol_Wine_Beer = 0
            alcohol_str = 'Full Bar'

        # 3) option for smoking area
        if smoking_area == 0:
            smoking_area_not_permitted = 0; smoking_area_only_at_bar = 0; smoking_area_permitted = 0; smoking_area_section = 0
            smoking_area_str = 'None'
        elif smoking_area == 1:
            smoking_area_not_permitted = 1; smoking_area_only_at_bar = 0; smoking_area_permitted = 0; smoking_area_section = 0
            smoking_area_str = 'Not permitted'
        elif smoking_area == 2:
            smoking_area_not_permitted = 0; smoking_area_only_at_bar = 0; smoking_area_permitted = 0; smoking_area_section = 1
            smoking_area_str = 'Section'
        elif smoking_area == 3:
            smoking_area_not_permitted = 0; smoking_area_only_at_bar = 0; smoking_area_permitted = 1; smoking_area_section = 0
            smoking_area_str = 'Permitted'
        else:
            smoking_area_not_permitted = 0; smoking_area_only_at_bar = 1; smoking_area_permitted = 0; smoking_area_section = 0
            smoking_area_str = 'Only at bar'

        # 4) option for dress code
        if dress_code == 0:
            dress_code_formal = 0; dress_code_informal = 1
            dress_code_str = 'Informal'
        elif dress_code == 1:
            dress_code_formal = 0; dress_code_informal = 0
            dress_code_str = 'Casual'
        else:
            dress_code_formal = 1; dress_code_informal = 0
            dress_code_str = 'Formal'

        # 5) option for price
        if price == 0:
            price_low = 0; price_medium = 1
            price_str = 'Medium'
        elif price == 1:
            price_low = 1; price_medium = 0
            price_str = 'Low'
        else:
            price_low = 0; price_medium = 0
            price_str = 'High'
        
        # 6) option for Rambience
        if Rambience == 0:
            Rambience_quiet = 0
            Rambience_str = 'Familiar'
        else:
            Rambience_quiet = 1
            Rambience_str = 'Quiet'

        # 7) option for area
        if area == 0:
            area_open = 0
            area_str = 'Closed'
        else:
            area_open = 1
            area_str = 'Open'

        text = [city_str, alcohol_str, smoking_area_str, dress_code_str, price_str, Rambience_str, area_str]
        
        # machine learning rf_clf & prediction
        fitur = [
            city_Cuernavaca, city_Jiutepec, city_San_Luis_Potosi, city_Soledad,
            alcohol_No_Alcohol_Served, alcohol_Wine_Beer,
            smoking_area_not_permitted, smoking_area_only_at_bar, smoking_area_permitted, smoking_area_section,
            dress_code_formal, dress_code_informal,
            price_low, price_medium,
            Rambience_quiet,
            area_open
        ]

        prediksi = rf_clf.predict([fitur])[0]

        # set up the recommender criterias
        resto_profile['criteria'] = resto_profile['city'].str.cat(
            resto_profile[['alcohol', 'smoking_area', 'dress_code', 'price', 'Rambience', 'area']],
            sep = ' '
        )

        # count crtierias
        model = CountVectorizer(tokenizer = lambda i: i.split(' '), analyzer = 'word')
        matrix_criteria = model.fit_transform(resto_profile['criteria'])
        # tipe_criteria = model.get_feature_names()
        # jumlah_criteria = len(tipe_criteria)
        # event_criteria = matrix_criteria.toarray()

        # cosine similarity
        score = cosine_similarity(matrix_criteria)

        # test model
        resto_fav = prediksi

        # take the index from resto_fav
        index_fav = resto_profile[resto_profile['name'] == resto_fav].index.values[0]

        # list all restaurants + cosine similarity score
        all_resto = list(enumerate(score[index_fav]))

        # show similar restaurant, sorted by score
        resto_similar = sorted(all_resto, key = lambda i: i[1], reverse = True)

        # list all resto filter by cosine similarity score > 80%
        resto_recom = []
        for i in resto_similar:
            if i[1] > 0.8:
                resto_recom.append(i)
            else:
                pass
        
        # show 5 datas randomly
        rekomendasi = random.choices(resto_recom, k = 5)

        list_rekom = []
        for i in rekomendasi:
            ambil_rekom = {}
            j = 0
            while j < 8:
                ambil_rekom['name'] = resto_profile.iloc[i[0]]['name'].title(),
                ambil_rekom['city'] = resto_profile.iloc[i[0]]['city'],
                ambil_rekom['alcohol'] = resto_profile.iloc[i[0]]['alcohol'],
                ambil_rekom['smoking_area'] = resto_profile.iloc[i[0]]['smoking_area'],
                ambil_rekom['dress_code'] = resto_profile.iloc[i[0]]['dress_code'],
                ambil_rekom['price'] = resto_profile.iloc[i[0]]['price'],
                ambil_rekom['Rambience'] = resto_profile.iloc[i[0]]['Rambience'],
                ambil_rekom['area'] = resto_profile.iloc[i[0]]['area']
                ambil_rekom['latitude'] = resto_profile.iloc[i[0]]['latitude']
                ambil_rekom['longitude'] = resto_profile.iloc[i[0]]['longitude']
                j += 1
            
            list_rekom.append(ambil_rekom)
        
        # print(list_rekom[0]['latitude'])

        # create map object
        m = folium.Map(location=[list_rekom[0]['latitude'], list_rekom[0]['longitude']], zoom_start=12)
        tooltip = 'Click For More Info'

        # create marker
        folium.Marker(
            [list_rekom[0]['latitude'], list_rekom[0]['longitude']],
            popup = list_rekom[0]['name'][0],
            tooltip = tooltip
        ).add_to(m)

        folium.Marker(
            [list_rekom[1]['latitude'], list_rekom[1]['longitude']],
            popup = list_rekom[1]['name'][0],
            tooltip = tooltip
        ).add_to(m)

        folium.Marker(
            [list_rekom[2]['latitude'], list_rekom[2]['longitude']],
            popup = list_rekom[2]['name'][0],
            tooltip = tooltip
        ).add_to(m)

        folium.Marker(
            [list_rekom[3]['latitude'], list_rekom[3]['longitude']],
            popup = list_rekom[3]['name'][0],
            tooltip = tooltip
        ).add_to(m)

        folium.Marker(
            [list_rekom[4]['latitude'], list_rekom[4]['longitude']],
            popup = list_rekom[4]['name'][0],
            tooltip = tooltip
        ).add_to(m)

        # generate map
        m.save('templates/map.html')

        return render_template('rekomendasi.html', text = text, rekom = list_rekom)
        
        # return redirect(url_for('show_prediction', prediksi = prediksi))
    else:        
        return render_template('home.html')

@app.route('/map')
def show_map():
    return render_template('map.html')

# @app.route('/result/<int:prediksi>')
# def show_prediction(prediksi):
#     print(prediksi)
#     if prediksi == 1:
#         return render_template('selamat.html')
#     else:
#         return render_template('mati.html')

if __name__ == '__main__':
    resto_profile = pd.read_csv('datasets/resto_profile.csv')
    rf_clf = joblib.load('model_restaurant')
    app.run(debug = True)