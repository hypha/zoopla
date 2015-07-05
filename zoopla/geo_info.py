import requests


class GeoInfo():
    def __init__(self, listing):
        self.listing = listing
        self.latitude = self.listing.latitude
        self.longitude = self.listing.longitude
        self.loc_info = self.geo_reverse()

    def geo_reverse(self):
        sensor = "true"

        base = "http://maps.googleapis.com/maps/api/geocode/json?"
        params = "latlng={lat},{lng}&sensor={sen}".format(
            lat=self.latitude,
            lng=self.longitude,
            sen=sensor)

        url = "{base}{params}".format(base=base, params=params)
        response = requests.get(url)
        try:
            return response.json()['results'][0]
        except IndexError:
            return "json_error"

    def post_code(self):
        return self.loc_info["address_components"][-1]["long_name"]

    def address(self):
        return self.loc_info["formatted_address"]





