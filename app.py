from flask import Flask, render_template, request, flash
import json
from mapModel import MapModel
from key import google_elevation_api_key
import osmnx as ox

app = Flask(__name__)
timeout = 500

@app.route('/', methods = ['GET','POST'])
def index():
    #print(request.method)
    if request.method == 'POST':
        slocation1 = request.form.get('slocation')
        elocation1 = request.form.get('elocation')
        ratio = request.form.get("%distance")
        minmax = request.form.get('minmax')

        mapcenter = request.form.get('mapcenter')[7:-1]
        mapcenter1 = str(float(mapcenter.split(",")[0]))
        mapcenter2 = str(float(mapcenter.split(",")[1]))

        zoom = request.form.get('zoom')

        # if slocation1 == "" or elocation1 == "" or ratio == "" or minmax == "":
        #     print("Some input is None!")
        #     return render_template('index.html', isPath="false")

        # if float(ratio) < 100:
        #     print("Ratio should be greater than 100!")
        #     return render_template('index.html', isPath="false")


        try:
            slocation = slocation1[7:-1]
            elocation = elocation1[7:-1]
            orig = [float(slocation.split(",")[0]),float(slocation.split(",")[1])]
            dest = [float(elocation.split(",")[0]),float(elocation.split(",")[1])]
            
            model = MapModel(timeout=timeout)
            model.add_elevation_info(google_elevation_api_key)

            start = ox.get_nearest_node(model.G, orig)
            end = ox.get_nearest_node(model.G, dest)

            limit_ratio = float(ratio) / 100.0
            if minmax == "Min":
                inverse = False
            else:
                inverse = True

            path, coords, path_length, path_elevation_gain, sp_length, sp_elevation_gain = model.pathFinder.get_path(model.G, start, end, limit_ratio=limit_ratio, weight='height', inverse=inverse)
            #print(coords)
            path = [
                    {'lat':orig[0],'lng':orig[1]}
                    ]
            for node in coords:
                d = {'lat':node[1],'lng':node[0]}
                path.append(d)
            path.append({'lat':dest[0],'lng':dest[1]})

            pathJson = json.dumps(path,ensure_ascii=False)
            #print(pathJson)
            #print(zoom)
            return render_template('index.html',path=pathJson,isPath="true",mapcenter1=mapcenter1,mapcenter2=mapcenter2,
                zoom=zoom,cacheStart=slocation1,cacheEnd=elocation1,
                spLength=sp_length,spHeight=sp_elevation_gain,curLength=path_length,curHeight=path_elevation_gain,
                ratio=ratio, minmax=minmax)
        except:
            print("Some input are not valid")
            return render_template('index.html', isPath="false")

    return render_template('index.html', isPath="false")

