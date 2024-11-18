import pytest
from unittest.mock import Mock
from bson import ObjectId, errors

class TestArtists:
    def test_get_artists_empty(self, client, mock_db):
        """בדיקה שמחזירה רשימת אמנים ריקה"""
        mock_db.db.artists.find.return_value = []
        response = client.get('/api/artists')
        
        assert response.status_code == 200
        assert response.json == []
        mock_db.db.artists.find.assert_called_once()
    
    def test_get_artists_with_data(self, client, mock_db):
        """בדיקת קבלת רשימת אמנים עם נתונים"""
        mock_artists = [
            {"_id": ObjectId(), "name": "שלמה ארצי", "songs": []},
            {"_id": ObjectId(), "name": "עידן רייכל", "songs": []}
        ]
        mock_db.db.artists.find.return_value = mock_artists
        
        response = client.get('/api/artists')
        data = response.get_json()
        
        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]['name'] == "שלמה ארצי"
        assert data[1]['name'] == "עידן רייכל"
    
    def test_add_artist_success(self, client, mock_db):
        """בדיקת הוספת אמן בהצלחה"""
        mock_id = ObjectId()
        mock_result = Mock()
        mock_result.inserted_id = mock_id
        mock_db.db.artists.insert_one.return_value = mock_result
        
        response = client.post('/api/artists', json={"name": "שלמה ארצי"})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["id"] == str(mock_id)
        mock_db.db.artists.insert_one.assert_called_once_with({
            "name": "שלמה ארצי",
            "songs": []
        })
    
    def test_add_artist_no_name(self, client, mock_db):
        """בדיקת הוספת אמן ללא שם"""
        response = client.post('/api/artists', json={})
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "Artist name is required" in data["error"]
        mock_db.db.artists.insert_one.assert_not_called()
    
    def test_delete_artist_success(self, client, mock_db):
        """בדיקת מחיקת אמן בהצלחה"""
        artist_id = str(ObjectId())
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db.db.artists.delete_one.return_value = mock_result
        
        response = client.delete(f'/api/artists/{artist_id}')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        mock_db.db.artists.delete_one.assert_called_once_with({"_id": ObjectId(artist_id)})
    
    def test_delete_artist_not_found(self, client, mock_db):
        """בדיקת מחיקת אמן שלא קיים"""
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_db.db.artists.delete_one.return_value = mock_result
        
        response = client.delete(f'/api/artists/{str(ObjectId())}')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Artist not found" in data["error"]
    
    def test_delete_artist_invalid_id(self, client, mock_db):
        """בדיקת מחיקת אמן עם ID לא חוקי"""
        response = client.delete('/api/artists/invalid-id')
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "Invalid artist ID format" in data["error"]

    def test_get_artists_db_error(self, client, mock_db):
        """בדיקת שגיאת דאטהבייס בקבלת אמנים"""
        mock_db.db.artists.find.side_effect = Exception("DB Error")
        
        response = client.get('/api/artists')
        data = response.get_json()
        
        assert response.status_code == 500
        assert data["success"] is False
        assert "error" in data

    def test_delete_artist_db_error(self, client, mock_db):
        """בדיקת שגיאת דאטהבייס במחיקת אמן"""
        artist_id = str(ObjectId())
        mock_db.db.artists.delete_one.side_effect = Exception("DB Error")
        
        response = client.delete(f'/api/artists/{artist_id}')
        data = response.get_json()
        
        assert response.status_code == 500
        assert data["success"] is False
        assert "error" in data


class TestArtistSongs:
    def test_add_song_success(self, client, mock_db):
        """בדיקת הוספת שיר לאמן בהצלחה"""
        artist_id = str(ObjectId())
        mock_result = Mock()
        mock_result.matched_count = 1
        mock_db.db.artists.update_one.return_value = mock_result
        
        song_data = {
            "title": "מכתב לאחי",
            "duration": "4:30"
        }
        
        response = client.post(f'/api/artists/{artist_id}/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        mock_db.db.artists.update_one.assert_called_once()
    
    def test_add_song_missing_fields(self, client, mock_db):
        """בדיקת הוספת שיר עם שדות חסרים"""
        artist_id = str(ObjectId())
        
        # חסר duration
        song_data = {"title": "מכתב לאחי"}
        
        response = client.post(f'/api/artists/{artist_id}/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "Title and duration are required" in data["error"]
    
    def test_add_song_artist_not_found(self, client, mock_db):
        """בדיקת הוספת שיר לאמן שלא קיים"""
        mock_result = Mock()
        mock_result.matched_count = 0
        mock_db.db.artists.update_one.return_value = mock_result
        
        song_data = {
            "title": "מכתב לאחי",
            "duration": "4:30"
        }
        
        response = client.post(f'/api/artists/{str(ObjectId())}/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Artist not found" in data["error"]
    
    def test_delete_song_success(self, client, mock_db):
        """בדיקת מחיקת שיר בהצלחה"""
        artist_id = str(ObjectId())
        mock_db.db.artists.find_one.return_value = {
            "_id": ObjectId(artist_id),
            "name": "שלמה ארצי",
            "songs": [{"title": "מכתב לאחי", "duration": "4:30"}]
        }
        
        response = client.delete(f'/api/artists/{artist_id}/songs/0')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
    
    def test_delete_song_invalid_index(self, client, mock_db):
        """בדיקת מחיקת שיר עם אינדקס לא תקין"""
        artist_id = str(ObjectId())
        mock_db.db.artists.find_one.return_value = {
            "_id": ObjectId(artist_id),
            "name": "שלמה ארצי",
            "songs": []
        }
        
        response = client.delete(f'/api/artists/{artist_id}/songs/0')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Song index out of range" in data["error"]

    def test_add_song_db_error(self, client, mock_db):
        """בדיקת שגיאת דאטהבייס בהוספת שיר"""
        artist_id = str(ObjectId())
        mock_db.db.artists.update_one.side_effect = Exception("DB Error")
        
        song_data = {
            "title": "Test Song",
            "duration": "3:30"
        }
        
        response = client.post(f'/api/artists/{artist_id}/songs',
                             json=song_data)
        data = response.get_json()
        
        assert response.status_code == 500
        assert data["success"] is False
        assert "error" in data