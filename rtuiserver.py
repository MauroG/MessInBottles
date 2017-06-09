# ---------------------------------------------------------------------------
# RaytranUI
# ---------------------------------------------------------------------------
# Falsk placeholder:    <name> | <type:name>
# type:   int | float | path  (default: str)
#

import os
import socket
import path
import multiprocessing as mp
import werkzeug._compat
from flask import *

from py.rtutils import *
from py.scserver import SceneServer
from py.ssserver import SensorServer, SpectralServer


# ---------------------------------------------------------------------------
# RTUI
# ---------------------------------------------------------------------------

class RTServers:

    # -----------------------------------------------------------------------
    # Constants
    # -----------------------------------------------------------------------

    CONFIG = "config.json"

    # -----------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------

    def __init__(self):

        self.home_directory = path.path(os.path.dirname(__file__))
        """:type: path.path"""
        self.configuration = None
        """:type: dict"""
        self.host = None
        """:type: str"""

        self.scene_server = None
        """:type: SceneServer"""

        self.sensor_server = None
        """:type: SensorServer"""

        self.spectral_server = None
        """:type: SpectralServer"""
    #end

    def configure(self, configfile=None):
        if configfile is None:
            configfile = self.home_directory.joinpath(self.CONFIG)
        else:
            configfile = path.path(configfile)

        self.configuration = json_load(configfile)

        self.scene_server = SceneServer(self, "/scenes")
        self.sensor_server = SensorServer(self, "/sensors")
        self.spectral_server = SpectralServer(self, "/spectrals")

        self.host = socket.gethostbyname(socket.gethostname())

        print "Configured"
    #end

    def start(self):
        if self.configuration is None:
            raise RuntimeError("Not configured")
    #end

    # -----------------------------------------------------------------------
    # End
    # -----------------------------------------------------------------------

#end


class RTUI(Flask):

    # -----------------------------------------------------------------------
    # Constants
    # -----------------------------------------------------------------------

    CONFIG = "config.json"

    # -----------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------

    def __init__(self, import_name, static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False):

        Flask.__init__(self, import_name,
                       static_path=static_path,
                       static_url_path=static_url_path,
                       static_folder=static_folder,
                       template_folder=template_folder,
                       instance_path=instance_path,
                       instance_relative_config=instance_relative_config)

        self.home_directory = path.path(os.path.dirname(__file__))
        """:type: path.path"""
        self.configuration = None
        """:type: dict"""
        self.host = None
        """:type: str"""

        self.scene_server = None
        """:type: SceneServer"""

        self.sensor_server = None
        """:type: SensorServer"""

        self.spectral_server = None
        """:type: SpectralServer"""
    #end

    def configure(self, configfile=None):
        if configfile is None:
            configfile = self.home_directory.joinpath(self.CONFIG)
        else:
            configfile = path.path(configfile)

        self.configuration = json_load(configfile)

        self.scene_server = SceneServer(self, "/scenes")
        self.sensor_server = SensorServer(self, "/sensors")
        self.spectral_server = SpectralServer(self, "/spectrals")

        self.host = socket.gethostbyname(socket.gethostname())

        print "Configured"
    #end

    # -----------------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------------

    def run(self, host=None, port=None, debug=None, **options):
        """Start the web server, but before check if it is configured

        :param str host: ip to use. Default '127.0.0.1'
        :param integer port: port to use. Default 5000
        :param bool debug: if enable the debug mode of Flask
        :param dict options: other options passed to Flask
        """
        if self.configuration is None:
            raise RuntimeError("Not configured")
        if host is None:
            host = self.host

        Flask.run(self, host=host, port=port, debug=debug, **options)
    #end

#end


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

app = RTUI(__name__)

# ---------------------------------------------------------------------------
# "/" handler

@app.route('/')
def home():
    return redirect("raytranui.html")
#end


def jsonify(data):
    return json.dumps(data), 200, {"Content-type": "application/json"}
#end


# ---------------------------------------------------------------------------
# default url handler

@app.route('/<path:path>')
def default_handler(path=None):
    """Each path not handled is converted in a file path, relative to the home
    directory of the application

    :param str path: relative (unhandled) path
    :return: Flask response from file
    """
    abspath = app.home_directory.joinpath(path)
    if not abspath.exists():
        print "file '{0}' doesn't exists".format(abspath)

    return send_from_directory(app.home_directory, path)
#end


# ===========================================================================
# RESTful API
# ===========================================================================

# ---------------------------------------------------------------------------
# /
# /raytranui
#
# ---------------------------------------------------------------------------

@app.route("/")
@app.route("/raytranui")
def raytranui():
    return send_from_directory(app.home_directory, "raytranui.html")
#end


@app.route("/raytranui/<path:path>")
def rtui_file(path):
    return send_from_directory(app.home_directory, path)
#end


# ---------------------------------------------------------------------------
# /rtuimain
# ---------------------------------------------------------------------------

@app.route("/rtuimain")
def rtuimain():
    return send_from_directory(app.home_directory, "raytranui.json")
#end


# ---------------------------------------------------------------------------
# /scenes
# /scenes/<scene>
# /scenes/<scene>/info
# ---------------------------------------------------------------------------

@app.route("/scenes")
def scene_hierarchy():
    try:
        scenes = app.scene_server.scenes()
        return jsonify(scenes)
    except Exception as e:
        raise e
#end


@app.route("/scenes/<sceneId>")
@app.route("/scenes/<sceneId>/info")
def scene_info(sceneId):
    try:
        sceneId, variant = split_variant(sceneId)
        info = app.scene_server.scene_info(sceneId, variant)
        return jsonify(info)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /scenes/<scene>/spectrals
# /scenes/<scene>/spectrals/<spectral>
# ---------------------------------------------------------------------------

@app.route("/scenes/<sceneId>/spectrals")
def scene_spectrals(sceneId):
    try:
        sceneId, variant = split_variant(sceneId)
        spectrals = app.scene_server.scene_spectrals(sceneId)
        return jsonify(spectrals)
    except Exception as e:
        raise e
#end


@app.route("/scenes/<sceneId>/spectrals/<spectralId>")
def scene_spectral(sceneId, spectralId):
    try:
        sceneId, variant = split_variant(sceneId)
        spectral = app.scene_server.scene_spectral(sceneId, spectralId)
        return jsonify(spectral)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /sensors -> list of sensor categories
# /sensors/<category> -> list of sensors under the category
# /sensors/<category>/<sensor>/info -> sensor informations
# /sensors/<category>/<sensor>/bands -> list of sensor bands
# /sensors/<category>/<sensor>/bands/<band> -> band informations
# ---------------------------------------------------------------------------

def first_sensor(sensor_hierarchy):
    if len(sensor_hierarchy) == 0:
        return None
    elif len(sensor_hierarchy[0]["sensors"]) == 0:
        return None
    else:
        return sensor_hierarchy[0]["sensors"][0]["id"]
#end


@app.route("/sensors")
def sensor_hierarchy():
    try:
        # categories = app.sensor_server.categories()
        # return jsonify(categories)
        sensor_hierarchy = app.sensor_server.sensor_hierarchy()
        return jsonify({
            "sensors": sensor_hierarchy,
            "current": first_sensor(sensor_hierarchy)
        })
    except Exception as e:
        raise e
#end


@app.route("/sensors/<categoryId>")
def category_sensors(categoryId):
    try:
        sensors = app.sensor_server.sensors(categoryId)
        return jsonify(sensors)
    except Exception as e:
        raise e
#end


@app.route("/sensors/<categoryId>/<sensorId>")
def sensor_info(categoryId, sensorId):
    try:
        sinfo = app.sensor_server.sensor_info(categoryId, sensorId)
        return jsonify(sinfo)
    except Exception as e:
        raise e
#end


@app.route("/sensors/<categoryId>/<sensorId>/<band>")
def band_info(categoryId, sensorId, band):
    try:
        binfo = app.sensor_server.band_info(categoryId, sensorId, band)
        return jsonify(binfo)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /spectrals
# ---------------------------------------------------------------------------

@app.route("/spectrals")
def spectral_hierarchy():
    try:
        # categories = app.spectral_server.categories()
        # return jsonify(categories)
        spectral_hierarchy = app.spectral_server.spectral_hierarchy()
        return jsonify({
            "categories": spectral_hierarchy,
            "current": spectral_hierarchy[0]["id"] if len(spectral_hierarchy) > 0 else None
        })
    except Exception as e:
        raise e
#end


@app.route("/spectrals/<path:spectralId>")
def category_spectrals(spectralId):
    try:
        spectrals = app.spectral_server.spectrals(spectralId)
        return jsonify(spectrals)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /images
# /images/<scene>
# /images/<scene>/<collectionId>
# ---------------------------------------------------------------------------


@app.route("/images")
def image_hierarchy():
    try:
        images = app.scene_server.image_hierarchy()
        return jsonify(images)
    except Exception as e:
        raise e
#end


@app.route("/images/<sceneId>", defaults={"collectionId": ""})
@app.route("/images/<sceneId>/<path:collectionId>")
def scenes_images(sceneId, collectionId):
    try:
        sceneId, variant = split_variant(sceneId)
        if is_image(collectionId):
            image = app.scene_server.scene_image(sceneId, collectionId);
            return send_file(image.path(), image.mimetype())
        else:
            images = app.scene_server.scene_images(sceneId, collectionId)
            return jsonify(images)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /simulations
# ---------------------------------------------------------------------------

@app.route("/simulations")
def simulation_hierarchy():
    try:
        simulations = app.scene_server.simulation_hierarchy()
        return jsonify(simulations)
    except Exception as e:
        raise e
#end


@app.route("/simulations/<sceneId>", defaults={"simulationId": ""})
@app.route("/simulations/<sceneId>/<path:simulationId>")
def simulation_measures(sceneId, simulationId):
    try:
        if is_measure(simulationId):
            measure = app.scene_server.simulation_measure(sceneId, simulationId)
            return send_file(measure.path(), "text/plain" if not measure.binary() else "application/octet-stream")
        else:
            measures = app.scene_server.simulation_measures(sceneId, simulationId)
            return jsonify(measures)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# /simtree
# ---------------------------------------------------------------------------

@app.route("/simtree", methods=['GET', 'POST'])
def simtree_node():

    def head(s):
        if s is None: s = ""
        p = s.find("/")
        return s if p == -1 else s[0:p]

    def tail(s):
        if s is None: s = ""
        p = s.find("/")
        return "" if p == -1 else s[p+1:]

    try:
        id = request.form.get("id")
        simulations = app.scene_server.simulation_node(head(id), tail(id))
        return jsonify(simulations)
    except Exception as e:
        raise e
#end


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.configure()
    #app.run(host="127.0.0.1", debug=True)
    #app.run(host="192.168.0.3", debug=True, processes=4)
    # app.run(debug=True)
    # app.run(debug=False, processes=8)
    app.run()
#end
