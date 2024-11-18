import pytest
from unittest.mock import Mock
from bson import ObjectId

class TestFavorites:
    def test_get_favorites_empty(self, client, mock_db):
        """בדיקת קבלת רשימת מועדפים ריקה"""
        mock_db.db.favorites.find_one.return_value = None
        
        response = client.get('/api/favorites')
        data = response.get_json()
        
        assert response.status_code == 200
        assert "songs" in data
        assert len(data["songs"]) == 0
    
    def test_get_favorites_with_songs(self, client, mock_db):
        """בדיקת קבלת רשימת מועדפים עם שירים"""
        mock_favorites = {
            "_id": ObjectId(),
            "type": "user_favorites",
            "songs": [
                {
                    "artist_id": str(ObjectId()),
                    "artist_name": "שלמה ארצי",
                    "title": "מכתב לאחי",
                    "duration": "4:30"
                }
            ]
        }
        mock_db.db.favorites.find_one.return_value = mock_favorites
        
        response = client.get('/api/favorites')
        data = response.get_json()
        
        assert response.status_code == 200
        assert len(data["songs"]) == 1
        assert data["songs"][0]["title"] == "מכתב לאחי"
    
    def test_add_favorite_song_success(self, client, mock_db):
        """בדיקת הוספת שיר למועדפים"""
        # הגדרת Mock להוספה ראשונית של מסמך המועדפים
        mock_update_result = Mock()
        mock_update_result.matched_count = 1
        mock_db.db.favorites.update_one.return_value = mock_update_result
        
        song_data = {
            "artist_id": str(ObjectId()),
            "artist_name": "עידן רייכל",
            "title": "מילים",
            "duration": "4:20"
        }
        
        response = client.post('/api/favorites/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
    
    def test_add_favorite_song_missing_fields(self, client, mock_db):
        """בדיקת הוספת שיר למועדפים עם שדות חסרים"""
        song_data = {
            "title": "מילים",
            "duration": "4:20"
        }
        
        response = client.post('/api/favorites/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "required" in data["error"]
    
    def test_remove_favorite_song_success(self, client, mock_db):
        """בדיקת הסרת שיר מהמועדפים"""
        mock_result = Mock()
        mock_result.matched_count = 1
        mock_db.db.favorites.update_one.return_value = mock_result
        
        artist_id = str(ObjectId())
        song_title = "מילים"
        
        response = client.delete(f'/api/favorites/songs/{artist_id}/{song_title}')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        mock_db.db.favorites.update_one.assert_called_once()
    
    def test_remove_favorite_song_not_found(self, client, mock_db):
        """בדיקת הסרת שיר שלא קיים במועדפים"""
        mock_result = Mock()
        mock_result.matched_count = 0
        mock_db.db.favorites.update_one.return_value = mock_result
        
        response = client.delete(f'/api/favorites/songs/{str(ObjectId())}/not-exists')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Favorites not found" in data["error"]