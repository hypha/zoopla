#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'raquel'
import collections
import pandas as pd

from api_factory import api as API
from geo_info import GeoInfo
from map import Map
from flask import Flask, request
import json


def zoopla_list(area, listing_status,  minimum_beds,maximum_beds, minimum_price, maximum_price):
    listings = []
    api = API(version=1, api_key='k4uew92e27kzs7nbrk93uguh')
    for listing in api.property_listings(area=str(area),
                                         listing_status=listing_status,
                                         max_results=None,
                                         minimum_beds=minimum_beds,
                                         maximum_beds=maximum_beds,
                                         minimum_price=minimum_price,
                                         maximum_price=maximum_price):
        listings.append(listing)
    return listings

# get all of the listings, sort each  by keys


def sort_listing_dic(area, listing_status,  minimum_beds, maximum_beds, minimum_price, maximum_price):
    listings = zoopla_list(area, listing_status,  minimum_beds, maximum_beds, minimum_price, maximum_price)
    for listing in listings:
        if "new_home" not in listing.__dict__:
            listing.__dict__.update({"new_home": None})
            collections.OrderedDict(sorted(listing.__dict__.items()))
    return listings


def property_keys(properties):
    keys = properties[0].__dict__.keys()
    return sorted(keys)


def property_df(properties):
    df = pd.DataFrame(p.__dict__ for p in properties)
    return df


def property_location(properties):
    geo_listings = []
    for listing in properties:
        geo_listings.append(GeoInfo(listing))
    return geo_listings



# properties = sort_listing_dic("edinburgh", "sale", "2", "350000")
#
# locations_info = property_location(properties)
#
# postcodes = [x.postcode for x in locations_info]
# formatted_addresses = [x.address() for x in locations_info]
#
# prop_df = property_df(properties)
# locations = [x.loc_info for x in locations_info]
#
# prop_df["Postcode"] = postcodes
# prop_df["formatted_address"] = formatted_addresses
#
# dep_df = pd.ExcelFile("./Deprivation_Index_2016.xls")
#
# dep_full = dep_df.parse("All postcodes")
#
# zoopla_dep = prop_df.merge(dep_full, on=["Postcode"])
#
# df3 = zoopla_dep[["formatted_address", "details_url", "latitude", "longitude"]][zoopla_dep["SIMD16_Vigintile"] > 17]
#
# map = Map()
#
# for i in range(len(df3)):
#     map.add_point((df3.iloc[i].latitude, df3.iloc[i].longitude))
#
#
# with open("output1.html", "w") as out:
#     print(map, file=out)


def makemap(minmdi=8, min_price=150000, max_price=350000, loc="sutton, london", min_bed=0, max_bed=999):
    ## for london
    properties = sort_listing_dic(loc, "sale", min_bed, max_bed, min_price, max_price)
    locations_info = property_location(properties)

    postcodes = [x.postcode for x in locations_info]
    formatted_addresses = [x.address() for x in locations_info]

    prop_df = property_df(properties)
    locations = [x.loc_info for x in locations_info]

    prop_df["Postcode"] = postcodes
    prop_df["formatted_address"] = formatted_addresses


    dep_df = pd.ExcelFile("./sutton-deprivation-data.xlsx")
    dep_full = dep_df.parse("Sheet1")
    zoopla_dep = prop_df.merge(dep_full, on=["Postcode"])
    df3 = zoopla_dep.ix[:,][zoopla_dep["Index of Multiple Deprivation Decile"] >= minmdi]
    print(list(df3))
    map = Map()
    for i in range(len(df3)):
        description = """{addr}
£{price}
Bedrooms: {beds}
Deprivation: {mdi}""".format(addr=df3.iloc[i].formatted_address, price=df3.iloc[i].price, beds=df3.iloc[i].num_bedrooms,
                             mdi=df3.iloc[i]['Index of Multiple Deprivation Decile'])
        map.add_point((df3.iloc[i].latitude, df3.iloc[i].longitude, df3.iloc[i].details_url, json.dumps(description)))
    return str(map)



app = Flask(__name__)

@app.route('/map', methods=['POST', 'GET'])
def map_page():
    #print(request.values.keys())
    #print(makemap(minmdi=int(request.args.get('minmdi', 8))))
    #print("koko")
    return makemap(minmdi=int(request.args.get('min_mdi', 8)), min_price=int(request.args.get('min_price', 150000)),
                   max_price=int(request.args.get('max_price', 500000)), loc=request.args.get('loc', 'sutton, london'),
                   min_bed=int(request.args.get('min_bed', 0)), max_bed=int(request.args.get('max_bed', 999)))

@app.route('/form')
def form():
    return """<html>
<head></head><body><form action="/map" method="get" target="bottom">
<table><tr>
<th>Minimum Deprivation Index</th> <td>  <input type="range" name="min_mdi" min="0" max="10"  value="8"></td>
<th>Minimum Price</th><td><input type="text" name="min_price" value="150000"></td>
<th>Maximum Price</th><td><input type="text" name="max_price" value="400000"></td>
<th>Min. Bedrooms</th><td>
<select name="min_beds">
  <option value="0">Studio/None</option>
  <option value="1" selected>1</option>
  <option value="2">2</option>
  <option value="3">3</option>
</select>

<th>Max. Bedrooms</th><td>
<select name="max_beds">
  <option value="0">Studio/None</option>
  <option value="1">1</option>
  <option value="2">2</option>
  <option value="3" selected >3</option>
  <option value="999">4+</option>

</select>

<td><input type="submit" value="Update Map"></td>
</tr></table>
</form></body>"""

@app.route('/')
def index():
    return """<!DOCTYPE html>
<html>
<head>
<title>Oofy</title>
</head>
<frameset rows="10%,90%">
   <frame name="top" src="/form" />
   <frame name="bottom" src="/map?min_price=150000&max_price=400000&min_beds=1&max_beds=3&mdi=8" />
   <noframes>
   <body>
      Your browser does not support frames.
   </body>
   </noframes>
</frameset>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
