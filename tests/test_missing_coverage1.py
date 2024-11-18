import pytest
from unittest.mock import Mock, patch
from bson import ObjectId, errors
from pymongo.errors import OperationFailure
from flask import Flask

# הנחת עבודה היא שיש לנו app מוגדר
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    with patch('app.mongo') as mock_mongo:
        yield mock_mongo

class TestCoverage:

    def test_add_artist_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה add_artist"""
        mock_db.db.artists.insert_one.side_effect = Exception("Database error")
        response = client.post('/api/artists', json={"name": "Test Artist"})
        assert response.status_code == 400
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_add_song_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה add_song"""
        mock_db.db.artists.update_one.side_effect = Exception("Database error")
        artist_id = str(ObjectId())
        response = client.post(f'/api/artists/{artist_id}/songs', json={"title": "Test Song", "duration": "3:30"})
        assert response.status_code == 500
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_delete_song_success(self, client, mock_db):
        """בדיקה של החזרת תגובה מוצלחת בפונקציה delete_song"""
        artist_id = str(ObjectId())
        mock_db.db.artists.find_one.return_value = {
            "_id": ObjectId(artist_id),
            "songs": [{"title": "Song 1"}, {"title": "Song 2"}]
        }
        response = client.delete(f'/api/artists/{artist_id}/songs/1')
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_get_playlists_with_data(self, client, mock_db):
        """בדיקה של הלולאה על פלייליסטים בפונקציה get_playlists"""
        mock_db.db.playlists.find.return_value = [
            {"_id": ObjectId(), "name": "Playlist 1"},
            {"_id": ObjectId(), "name": "Playlist 2"}
        ]
        response = client.get('/api/playlists')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert all("name" in playlist for playlist in data)

    def test_get_playlist_invalid_id(self, client):
        """בדיקה של errors.InvalidId בפונקציה get_playlist"""
        response = client.get('/api/playlists/invalid_id')
        assert response.status_code == 400
        assert response.get_json()["success"] is False
        assert "Invalid playlist ID format" in response.get_json()["error"]

    def test_delete_playlist_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה delete_playlist"""
        mock_db.db.playlists.delete_one.side_effect = Exception("Database error")
        playlist_id = str(ObjectId())
        response = client.delete(f'/api/playlists/{playlist_id}')
        assert response.status_code == 500
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_add_song_to_playlist_invalid_id(self, client):
        """בדיקה של errors.InvalidId בפונקציה add_song_to_playlist"""
        response = client.post('/api/playlists/invalid_id/songs', json={
            "artist_id": str(ObjectId()),
            "artist_name": "Test Artist",
            "title": "Test Song",
            "duration": "3:30"
        })
        assert response.status_code == 400
        assert response.get_json()["success"] is False
        assert "Invalid playlist ID format" in response.get_json()["error"]

    def test_add_song_to_playlist_not_found(self, client, mock_db):
        """בדיקה של פלייליסט לא נמצא בפונקציה add_song_to_playlist"""
        mock_db.db.playlists.update_one.return_value.matched_count = 0
        playlist_id = str(ObjectId())
        response = client.post(f'/api/playlists/{playlist_id}/songs', json={
            "artist_id": str(ObjectId()),
            "artist_name": "Test Artist",
            "title": "Test Song",
            "duration": "3:30"
        })
        assert response.status_code == 404
        assert response.get_json()["success"] is False
        assert "Playlist not found" in response.get_json()["error"]

    def test_remove_song_from_playlist_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה remove_song_from_playlist"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.return_value = {
            "_id": ObjectId(playlist_id),
            "songs": [{"title": "Song 1"}]
        }
        mock_db.db.playlists.update_one.side_effect = Exception("Database error")
        response = client.delete(f'/api/playlists/{playlist_id}/songs/0')
        assert response.status_code == 500
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_get_favorites_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה get_favorites"""
        mock_db.db.favorites.find_one.side_effect = Exception("Database error")
        response = client.get('/api/favorites')
        assert response.status_code == 500
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_add_favorite_song_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה add_favorite_song"""
        mock_db.db.favorites.update_one.side_effect = Exception("Database error")
        response = client.post('/api/favorites/songs', json={
            "artist_id": str(ObjectId()),
            "artist_name": "Test Artist",
            "title": "Test Song",
            "duration": "3:30"
        })
        assert response.status_code == 400
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_remove_favorite_song_exception(self, client, mock_db):
        """בדיקה של Exception בפונקציה remove_favorite_song"""
        mock_db.db.favorites.update_one.side_effect = Exception("Database error")
        artist_id = str(ObjectId())
        title = "Test Song"
        response = client.delete(f'/api/favorites/songs/{artist_id}/{title}')
        assert response.status_code == 500
        assert response.get_json()["success"] is False
        assert "Database error" in response.get_json()["error"]

    def test_validate_json_exception(self, client):
        """בדיקה של Exception בפונקציה validate_json"""
        with patch('flask.Request.get_json', side_effect=Exception("JSON parsing error")):
            response = client.post('/api/artists', data='{"name": "Test Artist"}', content_type='application/json')
            assert response.status_code == 400
            assert response.get_json()["success"] is False
            assert "Invalid JSON format" in response.get_json()["error"]



