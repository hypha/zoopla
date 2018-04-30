import requests
import logging

logger = logging.getLogger('oofy')

class GeoInfo():
    def __init__(self, listing):
        self.listing = listing
        self.latitude = self.listing.latitude
        self.longitude = self.listing.longitude
        self.loc_info = self.geo_reverse()


    # given latitude and longitude
    def geo_reverse(self):
        sensor = "true"

        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = "latlng={lat},{lng}&sensor={sen}&key={key}".format(
            lat=self.latitude,
            lng=self.longitude,
            sen=sensor,
            key="AIzaSyCUheJjOrMCZT2VTw9hdeZKcMW9D8SNQek")

        url = "{base}{params}".format(base=base, params=params)
        response = requests.get(url)
        try:
            return response.json()['results'][0]
        except IndexError:
            return "json_error"

    def geo_search(self, address):
        address = address.replace(",", "").replace(" ", "+")+"+"+str(self.latitude)+"+"+str(self.longitude)
        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = "address={address}&key={key}".format(
            address=address,
            key="AIzaSyCUheJjOrMCZT2VTw9hdeZKcMW9D8SNQek")
        url = "{base}{params}".format(base=base, params=params)
        response = requests.get(url)
        try:
            self.loc_info = response.json()['results'][0]

        except IndexError:
            self.loc_info = "json_error"
        return self.loc_info

    def post_code(self):
        if self.loc_info != "json_error":
            return self.loc_info["address_components"][-1]["long_name"]
        else:
            return "json_error"

    def address(self):
        if self.loc_info != "json_error":
            return self.loc_info["formatted_address"]
        else:
            return "json_error"

    def incomplete_pc(self):
        postcode = self.post_code()
        if len(postcode) == 3 or len(postcode) == 4 or postcode == "json_error":
            return True

    def coordinate_pc_complete(self):
        self.geo_search(self.address())
        postcode = self.post_code()
        return postcode

    def address_pc_complete(self):
        ad = self.listing.displayable_address
        self.geo_search(ad)
        postcode = self.post_code()
        return postcode

    def complete_pc(self):

        if self.incomplete_pc():
            logger.debug( "%s: %3.4f, %3.4f" % (self.listing.displayable_address, self.latitude, self.longitude) )
            postcode = self.address_pc_complete()
        else:
            postcode = self.post_code()
        return postcode

