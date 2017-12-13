#!flask/bin/python
from flask import Flask, jsonify
import json
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.Yousicial

app = Flask(__name__)


@app.route('/api/v1/songs', methods=['GET'])
def get_songs():
    return jsonify({})

@app.route('/api/v1/songs/avg/difficulty', methods=['GET'])
def get_avg_difficuilty():
    return jsonify({})

@app.route('/api/v1/songs/search', methods=['GET'])
def get_search():
    return jsonify({})

@app.route('/api/v1/songs/rating', methods=['POST'])
def post_rating():
    return jsonify({})

@app.route('/api/v1//songs/avg/rating/<int:song_id>', methods=['GET'])
def get_song(song_id):
    return jsonify({})

if __name__ == '__main__':
    # if the database music is empty, load json file automaticlly
    if db.songs.count() == 0:
        songs = json.load(open('songs.json'))
        for song in songs:
            db.songs.insert(song)
    app.run(debug=True)