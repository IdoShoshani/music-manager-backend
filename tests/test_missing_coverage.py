import pytest
from unittest.mock import Mock, patch
from bson import ObjectId, errors
import json
from pymongo.errors import OperationFailure, DuplicateKeyError

class TestMissingCoverage:
    def test_json_decode_with_force(self, client):
        """בדיקת JSON לא תקין עם force=True"""
        response = client.post('/api/artists',
                             data='{"name": invalid}',
                             content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()["success"] is False
        assert "Invalid JSON format" in response.get_json()["error"]

    def test_invalid_object_id_initialization(self, client, mock_db):
        """בדיקת אתחול ObjectId לא תקין"""
        mock_db.db.artists.delete_one.side_effect = errors.InvalidId("Invalid ObjectId")
        response = client.delete('/api/artists/invalid_id')
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_failed_unset_operation(self, client, mock_db):
        """בדיקת כשלון בפעולת unset"""
        artist_id = str(ObjectId())
        mock_db.db.artists.find_one.return_value = {"_id": ObjectId(artist_id), "songs": [{"title": "test"}]}
        mock_db.db.artists.update_one.side_effect = OperationFailure("Unset operation failed")
        
        response = client.delete(f'/api/artists/{artist_id}/songs/0')
        assert response.status_code == 500
        assert response.get_json()["success"] is False

    def test_update_nonexistent_document(self, client, mock_db):
        """בדיקת עדכון מסמך לא קיים"""
        artist_id = str(ObjectId())
        mock_db.db.artists.update_one.return_value = Mock(matched_count=0)
        song_data = {"title": "test", "duration": "3:30"}
        
        response = client.post(f'/api/artists/{artist_id}/songs', json=song_data)
        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_invalid_index_unset(self, client, mock_db):
        """בדיקת אינדקס לא תקין בunset"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.return_value = {"_id": ObjectId(playlist_id), "songs": []}
        response = client.delete(f'/api/playlists/{playlist_id}/songs/999')
        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_playlist_duplicate_update(self, client, mock_db):
        """בדיקת עדכון כפול של פלייליסט"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.update_one.side_effect = DuplicateKeyError("Duplicate key error")
        song_data = {
            "artist_id": str(ObjectId()),
            "artist_name": "Test",
            "title": "Test",
            "duration": "3:30"
        }
        response = client.post(f'/api/playlists/{playlist_id}/songs', json=song_data)
        assert response.status_code == 500
        assert response.get_json()["success"] is False

    def test_playlist_remove_songs_operation_failure(self, client, mock_db):
        """בדיקת כשלון בהסרת שירים מפלייליסט"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.return_value = {"_id": ObjectId(playlist_id), "songs": [{"title": "test"}]}
        mock_db.db.playlists.update_one.side_effect = OperationFailure("Remove operation failed")
        
        response = client.delete(f'/api/playlists/{playlist_id}/songs/0')
        assert response.status_code == 500
        assert response.get_json()["success"] is False

    def test_favorites_invalid_update(self, client, mock_db):
        """בדיקת עדכון לא תקין במועדפים"""
        mock_db.db.favorites.update_one.side_effect = OperationFailure("Invalid update operation")
        song_data = {
            "artist_id": str(ObjectId()),
            "artist_name": "Test",
            "title": "Test",
            "duration": "3:30"
        }
        response = client.post('/api/favorites/songs', json=song_data)
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_favorites_remove_nonexistent(self, client, mock_db):
        """בדיקת הסרת שיר לא קיים מהמועדפים"""
        mock_db.db.favorites.update_one.return_value = Mock(matched_count=0)
        artist_id = str(ObjectId())
        response = client.delete(f'/api/favorites/songs/{artist_id}/nonexistent')
        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_favorites_remove_operation_failure(self, client, mock_db):
        """בדיקת כשלון בהסרת שיר מהמועדפים"""
        artist_id = str(ObjectId())
        mock_db.db.favorites.update_one.side_effect = OperationFailure("Remove operation failed")
        response = client.delete(f'/api/favorites/songs/{artist_id}/test')
        assert response.status_code == 500
        assert response.get_json()["success"] is False


class TestValidationErrors:
    def test_force_json_parse(self, client):
        """בדיקת פרסור JSON עם force=True"""
        response = client.post('/api/artists',
                             data='{"name": "test"',  # JSON לא תקין - חסר סוגר
                             content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_unset_invalid_field(self, client, mock_db):
        """בדיקת unset על שדה לא קיים"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.update_one.side_effect = OperationFailure("Cannot unset nonexistent field")
        response = client.delete(f'/api/playlists/{playlist_id}/songs/0')
        assert response.status_code == 500
        assert response.get_json()["success"] is False