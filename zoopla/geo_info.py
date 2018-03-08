import requests


class GeoInfo():
    def __init__(self, listing):
        self.listing = listing
        self.latitude = self.listing.latitude
        self.longitude = self.listing.longitude
        self.loc_info = self.geo_reverse()
        self.postcode = self.complete_pc()

    # given latitude and longitude
    def geo_reverse(self):
        sensor = "true"

        base = "http://maps.googleapis.com/maps/api/geocode/json?"
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
        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = "address={address}".format(
            address=address)
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
        if len(postcode) == 3 or len(postcode) == 4:
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
        postcode = self.post_code()
        if self.incomplete_pc():
            postcode = self.coordinate_pc_complete()
        if self.incomplete_pc():
            postcode = self.address_pc_complete()
        return postcode

