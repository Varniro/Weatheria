from flask import Flask,render_template, request
import requests;
from datetime import datetime
import sys
import io
import os
import seaborn as sns
from flask import Response
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True


app = Flask(__name__)

@app.route('/',methods =["GET", "POST"])

def index():
    print('Hello world!', file=sys.stderr)
    temp = ""
    zip = False
    tempData = []
    tData = []
    if request.method == "POST":
        # getting input with name = fname in HTML form
        city = request.form.get("city")
        if city[0] in str([0,1,2,3,4,5,6,7,8,9]):
            countryCode = request.form.get("cCode")
            zip = True
        if(zip==False):
            loc = requests.get("http://api.openweathermap.org/geo/1.0/direct?q="+ city+ ",{country code}&limit=1&appid="+os.getenv("OpenWeather_Key"))
            lat = loc.json()[0]["lat"]
            lon = loc.json()[0]["lon"]
            cityName = loc.json()[0]['name']
        else:
            loc = requests.get("http://api.openweathermap.org/geo/1.0/zip?zip="+ city+","+ countryCode+"&limit=1&appid="+os.getenv("OpenWeather_Key"))
            lat = loc.json()["lat"]
            lon = loc.json()["lon"]
            cityName = loc.json()['name']
        res = requests.get("https://api.openweathermap.org/data/2.5/forecast?lat="+str(lat)+"&lon="+str(lon)+"&appid="+os.getenv("OpenWeather_Key")+"&units=metric")
        data = res.json()
        stIndex = 0
        for x in range(0,data["cnt"],4):
            dates = data['list'][x]['dt_txt']
            if dates.endswith('21:00:00') or dates.endswith('09:00:00'):
                stIndex = x
                break

        for y in range(stIndex,data["cnt"],4):
            tempData.append(data['list'][y]['dt_txt'])
            tData.append(float(data['list'][y]['main']['temp']))

        tempData.pop(0)
        tData.pop(0)
        return render_template('index.html',city = cityName, temp = tempData, tData = tData,  lang = tData,currTemp = data['list'][0]['main']['temp'], min = data['list'][0]['main']['temp_min'], max = data['list'][0]['main']['temp_max'], fl = data['list'][0]['main']['feels_like'],weather = data['list'][0]['weather'][0]['main'], rec = True)

    return render_template('index.html', rec = False)

@app.route('/plot.png/<tempData>/<tData>')
def plot_png(tempData, tData):
   fig = Figure()
   axis = fig.add_subplot(1, 1, 1)
   print(type(tempData), file=sys.stderr)
   print(tData, file=sys.stderr)
   xs = list(tempData.split(',')[1:-1])
   tData = tData.split(",")
   tData = tData[1:-1]
   tData = list(map(float,tData))
   ys = list(tData)

   fig,ax=plt.subplots(figsize=(6,6))
   ax=sns.set(style="darkgrid")
#    ax.set(xlabel='common xlabel', ylabel='common ylabel')
   sns.barplot(x=ys,y=xs)
   plt.xlabel("Temperature (in Degree Celsius)")
   plt.ylabel("Date and Time(DD-MM-YY, 24-Hour Format)")
   canvas=FigureCanvas(fig)
   img = io.BytesIO()
   fig.savefig(img)
   img.seek(0)
   return Response(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)