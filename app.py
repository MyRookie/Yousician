#!flask/bin/python
from flask import Flask, jsonify, request
import json
import pymongo
from pymongo import MongoClient
from flask_restful import Resource, Api, reqparse
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client.Yousicial

app = Flask(__name__)
api = Api(app)

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.errorhandler(400)
def bad_request(error=None):
    message = {
            'status': 400,
            'message': 'Bad requesr: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp

@app.errorhandler(500)
def internal_server_error(error=None):
    message = {
            'status': 500,
            'message': 'Internal server error: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp

class GetSongs(Resource):
    def get(self):
        try:
            count = db.songs.count()
            idx = 0
            data = []
            while idx < count:
                songs = db.songs.find()[idx:idx+5]
                page = []
                for song in songs:
                    song['_id'] = str(song['_id'])
                    page.append(song)
                data.append({
                    'page_number': idx / 5 + 1,
                    'songs': page
                })
                idx += 5
            return jsonify(data)
        except:
            return internal_server_error()

class GetDifficuilty(Resource):
    def get(self):
        try:
            level = request.args.get('level')
            count = db.songs.count()
            pipe = [{'$group': {'_id': None, 'total': {'$sum': '$difficulty'}}}]
            if level is not None:
                level = int(level)
                pipe = [{"$match": {'level':level}}, {'$group': {'_id': None, 'total': {'$sum': '$difficulty'}}}]
                count = db.songs.count({'level':level})
                if count == 0:
                    return not_found()
            total_score = list(db.songs.aggregate(pipeline=pipe))[0]['total']
            avg = total_score / count
            return jsonify({'average': avg})
        except:
            return internal_server_error()

class SearchSongsByName(Resource):
    def get(self):
        try:
            message = request.args.get('message')
            if message is None:
                return bad_request()
            songs = db.songs.find({"title" : {'$regex' : message, '$options':"$i"}})
            data = []
            for song in songs:
                song['_id'] = str(song['_id'])
                data.append(song)
            return jsonify(data)
        except:
            return internal_server_error()

class SetRating(Resource):
    def post(self):
        try:
            # invalid id
            song_id = request.form['song_id']
            rating = int(request.form['rating'])
            try:
                sid = ObjectId(song_id)
            except:
                return not_found()
            if rating < 1 or rating > 5:
                return bad_request()
            if db.songs.count({"_id":sid}) == 0:
                return not_found()
            data = {
                'song_id': song_id,
                'rating': rating
            }
            db.rating.insert(data)
            for r in db.rating.find():
                print(r)
            return jsonify({"message":"submitted"})
        except:
            return internal_server_error()

class GetRating(Resource):
    def get(self, song_id):
        try:
            count = db.rating.count({"song_id":song_id})
            if count == 0:
                return not_found()
            pipe = [{"$match": {'song_id':song_id}}, {'$group': {'_id': None, 'total': {'$sum': '$rating'}}}]
            total_score = list(db.rating.aggregate(pipeline=pipe))[0]['total']
            average = total_score / count
            low = db.rating.find({"song_id":song_id}).sort([("rating", pymongo.ASCENDING)])[0]['rating']
            high = db.rating.find({"song_id":song_id}).sort([("rating", pymongo.DESCENDING)])[0]['rating']
            return jsonify({
                'average': average,
                'low': low,
                'high': high
            })
        except:
            return internal_server_error()

api.add_resource(GetSongs, '/api/v1/songs')
api.add_resource(GetDifficuilty, '/api/v1/songs/avg/difficulty')
api.add_resource(SearchSongsByName, '/api/v1/songs/search')
api.add_resource(SetRating, '/api/v1/songs/rating')
api.add_resource(GetRating, '/api/v1//songs/avg/rating/<string:song_id>')


if __name__ == '__main__':
    # if the database music is empty, load json file automaticlly
    if db.songs.count() == 0:
        songs = json.load(open('songs.json'))
        for song in songs:
            db.songs.insert(song)
    app.run(debug=True)