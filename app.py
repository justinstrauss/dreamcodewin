# Justin Strauss and Angela Lin
# Software Development Period 7
# API Project

from flask import Flask, render_template, request, redirect, session, url_for, flash
import urllib2, json, urllib, math, time, string
key = 'AIzaSyBun2m9jaQTFGb0qtR7Shh7inqFhzKbLL4'

app = Flask(__name__)
app.secret_key = "don't store this on github"

@app.route('/', methods=["POST","GET"])
@app.route('/index', methods=["POST","GET"])
def index():
        if request.method=="POST":
                flashed = False
		# read form data
		origin = request.form["origin"]
		destination = request.form["destination"]
                
                if origin != '' and destination != '':
                        # find the latitude and longitude of the origin and destination
                        geo1=geo_loc(origin)
                        geo2=geo_loc(destination)
                        
                        # flash error messages if entry is bogus
                        if isinstance(geo1, basestring):
                                flash(geo1)
                                flashed = True
                        if isinstance(geo2, basestring):
                                flash(geo2)
                                flashed = True
                        if flashed:
                                return redirect('/')

                        # gets a dictionary corresponding to the closest Citibike station
                        station1 = closestStation(geo1)
                        station2 = closestStation(geo2)
                        
                        # get dictionaries of Google Map route info for walking/bicycling
                        rlist1 = getGoogleJSON(urllib.quote_plus(origin),station1,"walking")
                        rlist2 = getGoogleJSON(station1,station2,"bicycling")

                        rlist3 = getGoogleJSON(station2,urllib.quote_plus(destination), "walking")
                        # flash error messages and redirect if a route doesn't exist
                        if isinstance(rlist1, basestring):
                                flash(rlist1)
                                flashed = True
                        if isinstance(rlist3, basestring):
                                flash(rlist3)
                                flashed = True
                        if flashed:
                                return redirect("/")

                        # use the dictionaries to get the distance for each leg of the Citibike trip
                        d1 = rlist1[0]['legs'][0]['distance']['value']
                        d3 = rlist3[0]['legs'][0]['distance']['value']

                        # flash error messages if the walk is too far
                        if d1 > 1000:
                                flash(origin + " is over a kilometer walk from the closest Citibike station.")
                                flashed = True
                        if d3 > 1000:
                                flash(destination + " is over a kilometer walk from the closest Citibike station.")
                                flashed = True
                        if flashed:
                                flash("Please use locations within the current Citibike Service area!")
                                return redirect("/")

                        #d1 = rlist1[0]['legs'][0]['distance']['text']
                        #d2 = rlist2[0]['legs'][0]['distance']['text']
                        #d3 = rlist3[0]['legs'][0]['distance']['text']

                        t1 = rlist1[0]['legs'][0]['duration']['text']
                        t2 = rlist2[0]['legs'][0]['duration']['text']
                        t3 = rlist3[0]['legs'][0]['duration']['text']
                        tsum = int(t1[:string.find(t1," ")]) + int(t2[:string.find(t2," ")]) + int(t3[:string.find(t3," ")])

                        steps1 = rlist1[0]['legs'][0]['steps']
                        #print steps1
                        #s1 = [i['html_instructions'] for i in steps1]
                        latlong1_s = [reverse_geo(i['start_location']) for i in steps1]
                        
                        latlong1_e = [reverse_geo(i['end_location']) for i in steps1]
                        steps2 = rlist2[0]['legs'][0]['steps']
                        #s2 = [i['html_instructions'] for i in steps2]
                        #print s2
                        latlong2 = [reverse_geo(i['start_location']) for i in steps1]
                        steps3 = rlist3[0]['legs'][0]['steps']
                        s3 = [i['html_instructions'] for i in steps3]
                        #print s3

                        rlistT = getGoogleJSON(urllib.quote_plus(origin), urllib.quote_plus(destination), "transit")

                        # stepsT1 = rlistT[0]['legs'][0]['steps'][0]['steps']
                        # T1 = [i['html_instructions'] for i in stepsT1]

                        # stepsT3 = rlistT[0]['legs'][0]['steps'][2]['steps']
                        # T3 = [i['html_instructions'] for i in stepsT3]
                        return render_template("result.html", 
                                               tsum=tsum, 
                                               rlist1=rlist1, 
                                               rlist2=rlist2, 
                                               rlist3=rlist3,
                                               rlistT=rlistT)
                else: #Both not filled out
                        flash("Please fill out the required fields.")
                        flashed = True
                        return redirect("/")
	else: #GET METHOD
		return render_template("index.html")

@app.route('/about')
def about():
	return render_template("about.html")

#given a dictionary with lng and lat to find approximate address
def reverse_geo(ldic):
        googleurl = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&key=%s" % (ldic['lat'], ldic['lng'], key)
        request = urllib2.urlopen(googleurl)
	result = request.read()
	d = json.loads(result)
        rdic = d['results'][0]
        address = rdic['formatted_address']
        address = urllib.quote_plus(address)
        return address

def closestStation(geo):
# returns the dictionary entry of the closest Citibike station to a given address
        rlist = getCitiJSON()
        distances = [math.sqrt((geo['lng']-r['longitude'])**2 + (geo['lat']-r['latitude'])**2) for r in rlist]
        shortest = min(distances)
        index = distances.index(shortest)
        return rlist[index]

def geo_loc(location):
#finds the longitude and latitude of a given location parameter using Google's Geocode API
#return format is a dictionary with longitude and latitude as keys
	loc = urllib.quote_plus(location)
	googleurl = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (loc,key)
	request = urllib2.urlopen(googleurl)
	results = request.read()
	gd = json.loads(results) #dictionary
        if gd['status'] != "OK":
                return location+" is a bogus location! What are you thinking?"
        else:
                result_dic = gd['results'][0] #dictionary which is the first element in the results list
                geometry = result_dic['geometry'] #geometry is another dictionary
                loc = geometry['location'] #yet another dictionary
                return loc

def getCitiJSON():
# returns a dictionary of Citibike station information
	url = "http://www.citibikenyc.com/stations/json"
	request = urllib2.urlopen(url)
	result = request.read()
	d = json.loads(result)
	rlist = d['stationBeanList']
	return rlist

def getGoogleJSON(origin, destination, mode):
# returns a dictionary of Google Map route information
        org = origin
        dest = destination
        now = int(time.time())
        if isinstance(origin,dict):
                org = str(origin["latitude"])+","+str(origin["longitude"])
                origin = origin['stationName']
        if isinstance(destination,dict):
                dest = str(destination["latitude"])+","+str(destination["longitude"])
                destination = destination['stationName']
	url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&departure_time=%s&key=%s" % (org, dest, mode, now, key)
        request = urllib2.urlopen(url)
	result = request.read()
	d = json.loads(result)
	if d['status'] != "OK":
		return "No %s directions exist between %s and %s." %(mode, origin, destination)
	else:
		rlist = d['routes']
		return rlist

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
