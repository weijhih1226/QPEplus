from collections import OrderedDict
import geojson
from pyproj import Geod

GREAT_CIRCLE = Geod(ellps="WGS84")
CIRCLE_STEP = 1.0


def fxrange(start, stop, step):
    """xrange for float step."""
    if start > stop:
        start, stop = stop, start
    x = start
    while x < stop:
        yield x
        x += step


class POINT:
    def __init__(self, properties):
        for key, value in properties.items():
            setattr(self, key, value)

    def get_circle_data(self, distance: list[int]):
        __circle_data = list()
        for i_distance in distance:
            __circle_data.append(
                [
                    GREAT_CIRCLE.fwd(
                        self.Coordinate[0], self.Coordinate[1], x, i_distance * 1000
                    )[0:2]
                    for x in fxrange(0.0, 360.0, CIRCLE_STEP)
                ]
            )
        return __circle_data


def parse_coordinate(coordinate: str, geotype=None):
    if geotype is None:
        geotype = "Point"
    output = list()

    if geotype == "Point":
        # Point((-115.81, 37.24))
        lon, lat = coordinate.split(":")
        return [float(lon), float(lat)]
    if geotype in (
        "MultiPoint",
        "LineString",
    ):
        # MultiPoint([(-155.52, 19.61), (-156.22, 20.74), (-157.97, 21.46)])
        # LineString([(8.919, 44.4074), (8.923, 44.4075)])
        for single_point in coordinate.split(";"):
            lon, lat = single_point.split(":")
            output.append([float(lon), float(lat)])
        return output
    if geotype in ("Polygon",):
        # Polygon([[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.38, 57.322)]])
        for single_point in coordinate.split(";"):
            lon, lat = single_point.split(":")
            output.append([float(lon), float(lat)])
        return [output]


class AIRPLAIN(POINT):

    """存放颱風預報定位資訊的物件"""

    def __init__(self, position_data):
        self.STID = position_data.get("STID")
        self.ChName = position_data.get("ChName")
        self.EnName = position_data.get("EnName")
        self.geotype = position_data.get("GeoType")
        if position_data.get("Color"):
            self.Color = position_data.get("Color")
        self.Coordinate = parse_coordinate(
            position_data.get("Coordinate"), geotype=position_data.get("GeoType")
        )
        super(AIRPLAIN, self).__init__(self.get_properties())

    def _get_defined_properties(self):
        properties_data = OrderedDict(
            [
                (
                    "STID",
                    self.STID,
                ),
                (
                    "ChName",
                    self.ChName,
                ),
                (
                    "EnName",
                    self.EnName,
                ),
                # ("distance_3", self.get_circle_data([3]), ),
                # ("distance_8", self.get_circle_data([8]), ),
                # ("distance_16", self.get_circle_data([16]), ),
            ]
        )
        return properties_data

    def get_properties(self, keys=None):
        """取得要放在 geojson 的 properties 中的資訊"""
        if keys is None:
            return self._get_defined_properties()

        properties_data = OrderedDict(
            [
                (
                    ikey,
                    getattr(self, ikey),
                )
                for ikey in keys
            ]
        )
        return properties_data

    @property
    def circle_data(self):
        return self.get_circle_data([3, 8, 16])


def generate_airplane():
    """產生機場的 geojson 檔案，包含 3/8/16 的範圍"""
    with open("CAA/airplain.txt", "r") as fp:
        data = fp.readlines()

    header = [x.strip() for x in data[0].split(",")]

    for i in data[1:]:
        output = list()
        tmp = dict(
            (header[j], x)
            for j, x in enumerate(i.split(","))
            if header[j] not in (str(), None)
        )
        tmp = AIRPLAIN(tmp)
        point = geojson.Point(tmp.Coordinate)
        distance_3 = geojson.Polygon(tmp.get_circle_data([3]))
        distance_8 = geojson.Polygon(tmp.get_circle_data([8]))
        distance_16 = geojson.Polygon(tmp.get_circle_data([16]))
        output = geojson.FeatureCollection(
            features=[
                geojson.Feature(
                    geometry=distance_16,
                    properties=OrderedDict(
                        [
                            (
                                "distance",
                                "16km",
                            )
                        ]
                    ),
                    color_line="#DB7800",
                    fill_opacity="0.0",
                    line_weight="1",
                ),
                geojson.Feature(
                    geometry=distance_8,
                    properties=OrderedDict(
                        [
                            (
                                "distance",
                                "8km",
                            )
                        ]
                    ),
                    color_line="#DB7800",
                    fill_opacity="0.0",
                    line_weight="1",
                ),
                geojson.Feature(
                    geometry=distance_3,
                    properties=OrderedDict(
                        [
                            (
                                "distance",
                                "3km",
                            )
                        ]
                    ),
                    color_line="#DB7800",
                    fill_opacity="0.0",
                    line_weight="1",
                ),
                geojson.Feature(
                    geometry=point,
                    properties=tmp.get_properties(),
                    **{
                        "marker-icon": "local_airport",
                        "marker-type": "icon_circle_marker",
                        "marker-text": tmp.ChName,
                        "marker-size": "medium",
                        "marker-opacity": "1",
                        "marker-color": "transparent",
                        "marker-border": False,
                    },
                ),
            ]
        )
        with open("/tmp/abc/{}.json".format(tmp.STID), "w") as fp:
            geojson.dump(output, fp)


if __name__ == "__main__":
    generate_airplane()
