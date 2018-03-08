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


def makemap(listing_status = "rent", minmdi=1, min_price=50, max_price=150, loc="edinburgh", min_bed=0, max_bed=999):
    ## for london
    properties = sort_listing_dic(loc, listing_status, min_bed, max_bed, min_price, max_price)
    locations_info = property_location(properties)

    postcodes = [x.complete_pc() for x in locations_info]
    formatted_addresses = [x.address() for x in locations_info]

    prop_df = property_df(properties)
    locations = [x.loc_info for x in locations_info]

    prop_df["Postcode"] = postcodes
    prop_df["formatted_address"] = formatted_addresses

    if loc == "Sutton, London":
        dep_df = pd.ExcelFile("./sutton-deprivation-data.xlsx")
        dep_full = dep_df.parse("Sheet1")
        zoopla_dep = prop_df.merge(dep_full, on=["Postcode"])
        df3 = zoopla_dep.ix[:, ][zoopla_dep["Index of Multiple Deprivation Decile"] >= minmdi]
        df3.rename(columns={'Index of Multiple Deprivation Decile': 'MDI Decile'}, inplace=True)
    elif loc == "Edinburgh":
        dep_df = pd.ExcelFile("./Deprivation_Index_2016.xls")
        dep_full = dep_df.parse("All postcodes")
        zoopla_dep = prop_df.merge(dep_full, on=["Postcode"])
        df3 = zoopla_dep.ix[:,][zoopla_dep["SIMD16_Vigintile"] >= minmdi]
        df3.rename(columns={'SIMD16_Vigintile': 'MDI Vigintile'}, inplace=True)
    map = Map()
    if 'df3' in locals():
        for i in range(len(df3)):
            description = """{addr}
                            £{price}
                            Bedrooms: {beds}
                            Deprivation: {mdi}""".format(addr=df3.iloc[i].formatted_address, price=df3.iloc[i].price, beds=df3.iloc[i].num_bedrooms,
                                 mdi=df3.iloc[i]['MDI Vigintile'])
            map.add_point((df3.iloc[i].latitude, df3.iloc[i].longitude, df3.iloc[i].details_url, json.dumps(description)))
    return str(map)


app = Flask(__name__)
#app.config["APPLICATION_ROOT"] = "/oofy"

@app.route('/oofy/map', methods=['POST', 'GET'])
def map_page():
    #print(request.values.keys())
    #print(makemap(minmdi=int(request.args.get('minmdi', 8))))
    #print("koko")
    return makemap(listing_status=request.args.get('listing_status', "rent"),
                   minmdi=int(request.args.get('min_mdi', 8)),
                   min_price=int(request.args.get('min_price', 250)),
                   max_price=int(request.args.get('max_price', 650)),
                   loc=request.args.get('loc', 'edinburgh'),
                   min_bed=int(request.args.get('min_bed', 0)),
                   max_bed=int(request.args.get('max_bed', 999)))

@app.route('/oofy/form')
def form():
    return """<html>
<head></head><body><form action="/oofy/map" style="display:inline" method="get" target="bottom">
<table border="0" cellspacing="0" cellpadding="0"><tr>

<tr><td>Location
<select name="loc">
  <option value="Edinburgh" selected>Edinburgh</option>
  <option value="Sutton, London">Sutton, London</option>
  </select></td>

<tr><td>Location
<select name="listing_status">
  <option value="rent" selected >Rent</option>
  <option value="sale">Sale</option>
  </select></td>

<tr><td>Minimum Deprivation Index:  <input type="range"  name="min_mdi" min="1" max="20"  value="1"></td>
  <td>Minimum Price<input type="text" name="min_price" value="50"></td>
<td>Maximum Price<input type="text" name="max_price" value="150"></td>
<tr><td>Min. Bedrooms
<select name="min_bed">
  <option value="0">Studio/None</option>
  <option value="1" selected>1</option>
  <option value="2">2</option>
  <option value="3">3</option>
  </select></td>
<td>Max. Bedrooms
<select name="max_bed">
  <option value="0">Studio/None</option>
  <option value="1">1</option>
  <option value="2">2</option>
  <option value="3">3</option>
  <option value="999" selected >4+</option>
  </select></td>

<td><input type="submit" value="Update Map"></td>
</tr></table>
</form></body>"""

@app.route('/oofy/')
def index():
    return """<!DOCTYPE html>
<html>
<head>
<title>Oofy</title>
</head>
<frameset rows="15%,85%">
   <frame name="top" src="/oofy/form" />
   <frame name="bottom" src="/oofy/map?listing_status=rent&min_price=250&max_price=550&loc=edinburgh&min_bed=1&max_bed=3&mdi=8" />
   <noframes>
   <body>
      Your browser does not support frames.
   </body>
   </noframes>
</frameset>
</html>
"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
