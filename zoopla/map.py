class Map(object):
    def __init__(self):
        self._points = []

    def add_point(self, coordinates):
        self._points.append(coordinates)

    def marker_js(self, latitude=0,longtitude=0, target_url="http://www.planewalk.net", description="unknown property"):
        return """var marker = new google.maps.Marker({{
                position: new google.maps.LatLng({lat}, {lon}),
                map: map,
                optimized:false,
                title: {desc},
                url: "{url}"
                }});
                marker.addListener('click', function() {{
                    window.open(this.url);
                }});""".format(lat=latitude, lon=longtitude, url=target_url, desc=description)

    def __str__(self):
        centerLat = sum((x[0] for x in self._points)) / len(self._points)
        centerLon = sum((x[1] for x in self._points)) / len(self._points)
        markersCode = "\n".join(
            # ["""new google.maps.Marker({{
            #     position: new google.maps.LatLng({lat}, {lon}),
            #     map: map,
            #     title: <a href="{url}">Hello World!</a>
            #     }});"""
            [self.marker_js(latitude=x[0], longtitude=x[1], target_url=x[2], description=x[3]) for x in self._points])
        return """
            <script src="https://maps.googleapis.com/maps/api/js?key={key}&v=3.exp"></script>
            <div id="map-canvas" style="height: 100%; width: 100%"></div>
            <script type="text/javascript">
                var map;
                function show_map() {{
                    map = new google.maps.Map(document.getElementById("map-canvas"), {{
                        zoom: 13,
                        center: new google.maps.LatLng({centerLat}, {centerLon})
                    }});
                    {markersCode}
                }}
                google.maps.event.addDomListener(window, 'load', show_map);
            </script>
        """.format(centerLat=centerLat, centerLon=centerLon,
                   markersCode=markersCode, key="AIzaSyASjkgLegAeY8JUmyFz-RIQ0e_dRP8wg1A")
