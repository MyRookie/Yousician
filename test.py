import os
import app
import unittest
import tempfile
import json
from pymongo import MongoClient

class appTestCase(unittest.TestCase):

    def get_database(self):
        client = MongoClient('mongodb://localhost:27017/')
        return client.Yousician

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_wrong_url(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 404)

    def test_get_songs(self):
        response = self.app.get('/api/v1/songs')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)

    def test_get_difficuilty_no_level(self):
        response = self.app.get('/api/v1/songs/avg/difficulty')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['average'], 113.56 / 11)

    def test_get_difficuilty_level_not_exist(self):
        response = self.app.get('/api/v1/songs/avg/difficulty?level=10')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_get_difficuilty_with_level(self):
        response = self.app.get('/api/v1/songs/avg/difficulty?level=9')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['average'], 29.08 / 3)

    def test_get_difficuilty_with_message_can_be_found(self):
        response = self.app.get('/api/v1/songs/search?message=a')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 9)

    def test_get_difficuilty_with_message_can_not_be_found(self):
        response = self.app.get('/api/v1/songs/search?message=aaaaaa')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_post_valid_rating(self):
        db = self.get_database()
        sid = str(db.songs.find_one()['_id'])
        response = self.app.post('/api/v1/songs/rating', data=dict(song_id=sid, rating=2.5))
        self.assertEqual(response.status_code, 200)
        db.rating.delete_one({'song_id':sid, 'rating':2.5})

    def test_post_invalid_rating_larger(self):
        db = self.get_database()
        sid = str(db.songs.find_one()['_id'])
        response = self.app.post('/api/v1/songs/rating', data=dict(song_id=sid, rating=5.0001))
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_rating_smaller(self):
        db = self.get_database()
        sid = str(db.songs.find_one()['_id'])
        response = self.app.post('/api/v1/songs/rating', data=dict(song_id=sid, rating=0.999))
        self.assertEqual(response.status_code, 400)

    def test_post_to_invalid_song(self):
        response = self.app.post('/api/v1/songs/rating', data=dict(song_id='5a319d27a9ad9jv8d3434a80', rating=3))
        self.assertEqual(response.status_code, 404)

    def test_get_high_low_avg(self):
        db = self.get_database()
        sid = str(db.songs.find_one()['_id'])
        print(sid)
        response = self.app.post('/api/v1/songs/rating', data=dict(song_id=sid, rating=2.5))
        response = self.app.get('/api/v1//songs/avg/rating/'+sid)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        db.rating.delete_one({'song_id':sid, 'rating':2.5})

    def test_get_high_low_avg_invalid_id(self):
        response = self.app.get('/api/v1//songs/avg/rating/5a319d27a9ad9jv8d3434a80')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
    

if __name__ == '__main__':
    unittest.main()