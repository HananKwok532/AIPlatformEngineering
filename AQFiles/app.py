from flask import Flask, render_template, request
import tensorflow as tf
import keras
import loadmodels as lm
import random

app = Flask(__name__)

# Loading the models & weights
# NO2 model
global no2_model, no2_graph
no2_model, no2_graph = lm.loadno2()
# SO2 model
global so2_model, so2_graph
so2_model, so2_graph = lm.loadso2() 
# O3 model
global o3_model, o3_graph
o3_model, o3_graph = lm.loado3()
# CO model
global co_model, co_graph
co_model, co_graph = lm.loadco()

@app.route("/", methods=["GET"])
def home_page():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def predict_result():
    date = request.form["dateentry"] # Get the date entered by the user
    pol = request.form["polselect"] # Get the pollutant chosen by the user 
    avgconc = round(random.uniform(0, 100), 3) # Create a variable to store the predicted avg. concentration for a pollutant

    # Select the appropriate model based on the user's chosen pollutant
    if pol == 'NO2':
        print('NO2 Model')
        #with no2_graph.as_default():
        #    avgconc = no2_model.predict(date)
        #    print(avgconc)
    elif pol == 'SO2':
        print('SO2 Model')
    elif pol == 'O3':
        print('O3 Model')
    elif pol == 'CO':
        print('CO Model')

    avgconc_print = str(avgconc)
    if pol == 'NO2' or pol == 'SO2':
        avgconc_print += ' parts per billion'
    elif pol == 'O3' or pol == 'CO':
        avgconc_print += ' parts per million'
    
    return render_template("results.html", chosendate = date, pollutant = pol, avgconc = avgconc_print)

app.run(debug = True)