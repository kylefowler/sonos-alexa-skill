 # http://eca828d8.ngrok.io -> localhost:5000
 # python index.py --host=0.0.0.0
import time
import hashlib
import json

import requests
from flask import Flask, render_template, url_for, request

import soco
from soco import SoCo
from soco.music_services import MusicService

app = Flask(__name__)
app.debug = True

app.config.from_pyfile('settings.py')

speakers = soco.discover()

default_sonos = next(iter([x for x in speakers if x.player_name == app.config['DEFAULT_PLAYER']]), min(speakers))
app.config['active_sonos'] = default_sonos

print "Active sonos: " + app.config['active_sonos'].player_name

spotify = MusicService('Spotify')

def gen_sig():
    return hashlib.md5(
        app.config['ROVI_API_KEY'] +
        app.config['ROVI_SHARED_SECRET'] +
        repr(int(time.time()))).hexdigest()


def get_track_image(artist, album):
    blank_image = url_for('static', filename='img/blank.jpg')
    if 'ROVI_SHARED_SECRET' not in app.config:
        return blank_image
    elif 'ROVI_API_KEY' not in app.config:
        return blank_image

    headers = {
        "Accept-Encoding": "gzip"
    }
    req = requests.get(
        'http://api.rovicorp.com/recognition/v2.1/music/match/album?apikey=' +
        app.config['ROVI_API_KEY'] + '&sig=' + gen_sig() + '&name= ' +
        album + '&performername=' + artist + '&include=images&size=1',
        headers=headers)

    if req.status_code != requests.codes.ok:
        return blank_image

    result = json.loads(req.content)
    try:
        return result['matchResponse']['results'][0]['album']['images']\
            [0]['front'][3]['url']
    except (KeyError, IndexError):
        return blank_image


def getPlayer():
    return app.config['active_sonos']


@app.before_request
def setup_player():
    print "Handling player setup"
    player = request.args.get("location") if request.args.get("location", "None") != "None" else None
    if player is None or len(player) == 0:
        app.config['active_sonos'] = default_sonos
    else:
        for speak in speakers:
            if player.lower() in speak.player_name.lower():
                app.config['active_sonos'] = speak
                break


@app.route("/search")
def search():
    searchword = request.args.get('query', '')
    song = request.args.get('song') if request.args.get('song', "None") != "None" else None
    artist = request.args.get('artist') if request.args.get('artist', "None") != "None" else None

    if song != None and artist != None:
        print song, artist
        result = spotify.search(category='tracks', term=song)
    else:
        result = spotify.search(category='all', term=searchword)
    print result
    return 'Ok'


@app.route("/play")
def play():
    getPlayer().play()
    return 'Ok'


@app.route("/pause")
def pause():
    getPlayer().pause()
    return 'Ok'


@app.route("/next")
def nextTrack():
    getPlayer().next()
    return 'Ok'


@app.route("/previous")
def previous():
    getPlayer().previous()
    return 'Ok'


@app.route("/volume")
def volume():
    up = request.args.get('up', "True") == "True"
    if up:
        getPlayer().volume += 5
    else:
        getPlayer().volume -= 5

    return 'Ok'


@app.route("/info-light")
def info_light():
    track = getPlayer().get_current_track_info()
    return json.dumps(track)


@app.route("/info")
def info():
    print "Info from " + getPlayer().player_name
    track = getPlayer().get_current_track_info()
    track['image'] = get_track_image(track['artist'], track['album'])
    return json.dumps(track)


@app.route("/")
def index():
    track = getPlayer().get_current_track_info()
    track['image'] = get_track_image(track['artist'], track['album'])
    return render_template('index.html', track=track)


if __name__ == '__main__':
    app.run(debug=True)