from __future__ import print_function
__author__ = 'raquel'
import collections
import pandas as pd

from api_factory import api as API
from geo_info import GeoInfo
from map import Map

def zoopla_list(area, listing_status,  minimum_beds, maximum_price):
    listings = []
    api = API(version=1, api_key='k4uew92e27kzs7nbrk93uguh')
    for listing in api.property_listings(area=str(area),
                                         listing_status=listing_status,
                                         max_results=None,
                                         minimum_beds=minimum_beds,
                                         maximum_price=maximum_price):
        listings.append(listing)
    return listings

# get all of the listings, sort each  by keys


def sort_listing_dic(area, listing_status,  minimum_beds, maximum_price):
    listings = zoopla_list(area, listing_status,  minimum_beds, maximum_price)
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


def makemap():
    ## for london
    properties = sort_listing_dic("sutton, london", "sale", "2", "350000")
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
    df3 = zoopla_dep[["formatted_address", "details_url", "latitude", "longitude"]][zoopla_dep["Index of Multiple Deprivation Decile"] >= 8]
    map = Map()
    for i in range(len(df3)):
        map.add_point((df3.iloc[i].latitude, df3.iloc[i].longitude))
    return map

with open("output1.html", "w") as out:
    print(map, file=out)

