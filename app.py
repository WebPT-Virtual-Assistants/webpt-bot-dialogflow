
from __future__ import print_function
#from future.standard_library import install_aliases
#install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
from pip._vendor.requests.sessions import session

sessionForms = {}

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

#     print(req)

#     print("Request:")

#     print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)

#     print(res)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    print ("starting processRequest...", req.get("result").get("action"))
    res = None
    if sessionForms.get(req.get("sessionId")) == None:
        sessionForms[req.get("sessionId")] = "Session is: " + req.get("sessionId") + "\n"
    if req.get("result").get("action") == "initate_form.initate_form-name":
        res = processName(req)
    elif req.get("result").get("action") == "initate_form.initate_form-name.mechanism-of-injury-no":
        res = {}
        sessionForms[req.get("sessionId")] += "traumatic, lower extremity noncontact: No\n"
    elif "initate_form.initate_form-name.mechanism-of-injury-yes.pop-or-crack-no":
        res = {}
        sessionForms[req.get("sessionId")] += "pop Crack: No\n"
    elif "initate_form.initate_form-name.mechanism-of-injury-yes.pop-or-crack-yes":
        res = {}
        sessionForms[req.get("sessionId")] += "pop Crack: yes\n"
    elif req.get("result").get("action") == "initate_form.initate_form-name.mechanism-of-injury-yes":
        res = {}
        sessionForms[req.get("sessionId")] += "traumatic, lower extremity noncontact: Yes\n"
    elif req.get("result").get("action") == "initate_form.initate_form-name.mechanism-of-injury-yes.pop-or-crack-yes.swelling-yes":
        res = {}
        sessionForms[req.get("sessionId")] += "swelling: Yes\n"
    elif req.get("result").get("action") == "initate_form.initate_form-name.mechanism-of-injury-yes.pop-or-crack-yes.swelling-no":
        res = {}
        sessionForms[req.get("sessionId")] += "swelling: No\n"
    elif req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        #data = json.loads(result)
        #for some the line above gives an error and hence decoding to utf-8 might help
        data = json.loads(result.decode('utf-8'))
        res = makeWebhookResult(data)
        return res
    print(sessionForms[req.get("sessionId")])
    return res


def processName(req):
    result = req.get("result")
    session = req.get("sessionId")
    parameters = result.get("parameters")
    firstn = parameters.get("first-name")
    lastn = parameters.get("last-name")
    speech = "The name is " + firstn + " " + lastn + "\n"
    sessionForms[session] += speech
    return {
#         "speech": speech,
#         "displayText": speech,
#         # "data": data,
#         # "contextOut": [],
#         "source": "web-pt-webhook"
    }


# Weather Demo
# def processRequest(req):
#     print ("starting processRequest...",req.get("result").get("action"))
#     if req.get("result").get("action") != "yahooWeatherForecast":
#         return {}
#     baseurl = "https://query.yahooapis.com/v1/public/yql?"
#     yql_query = makeYqlQuery(req)
#     if yql_query is None:
#         return {}
#     yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
#     result = urlopen(yql_url).read()
#     #data = json.loads(result)
#     #for some the line above gives an error and hence decoding to utf-8 might help
#     data = json.loads(result.decode('utf-8'))
#     res = makeWebhookResult(data)
#     return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    print ("starting makeWebhookResult...")
    query = data.get('query')
    if query is None:
        return {}
 
    result = query.get('results')
    if result is None:
        return {}
 
    channel = result.get('channel')
    if channel is None:
        return {}
 
    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}
 
    condition = item.get('condition')
    if condition is None:
        return {}
 
    # print(json.dumps(item, indent=4))
 
    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')
 
#     print("Response:")
#     print(speech)
 
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

#     print("Starting app on port %d" % port)

app.run(debug=True, port=port, host='0.0.0.0')
