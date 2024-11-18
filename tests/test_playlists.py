import pytest
from unittest.mock import Mock
from bson import ObjectId

class TestPlaylists:
    def test_get_playlists_empty(self, client, mock_db):
        """בדיקת קבלת רשימת פלייליסטים ריקה"""
        mock_db.db.playlists.find.return_value = []
        
        response = client.get('/api/playlists')
        
        assert response.status_code == 200
        assert response.json == []
        mock_db.db.playlists.find.assert_called_once()
    
    def test_create_playlist_success(self, client, mock_db):
        """בדיקת יצירת פלייליסט חדש"""
        mock_id = ObjectId()
        mock_result = Mock()
        mock_result.inserted_id = mock_id
        mock_db.db.playlists.insert_one.return_value = mock_result
        
        playlist_data = {
            "name": "שירי קיץ",
            "description": "השירים הכי טובים לקיץ"
        }
        
        response = client.post('/api/playlists', json=playlist_data)
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        assert data["id"] == str(mock_id)
        mock_db.db.playlists.insert_one.assert_called_once_with({
            "name": "שירי קיץ",
            "description": "השירים הכי טובים לקיץ",
            "songs": []
        })
    
    def test_create_playlist_no_name(self, client, mock_db):
        """בדיקת יצירת פלייליסט ללא שם"""
        playlist_data = {"description": "תיאור כלשהו"}
        
        response = client.post('/api/playlists', json=playlist_data)
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "Playlist name is required" in data["error"]
        mock_db.db.playlists.insert_one.assert_not_called()
    
    def test_get_playlist_by_id_success(self, client, mock_db):
        """בדיקת קבלת פלייליסט לפי ID"""
        playlist_id = ObjectId()
        mock_playlist = {
            "_id": playlist_id,
            "name": "שירי קיץ",
            "description": "השירים הכי טובים לקיץ",
            "songs": []
        }
        mock_db.db.playlists.find_one.return_value = mock_playlist
        
        response = client.get(f'/api/playlists/{str(playlist_id)}')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["name"] == "שירי קיץ"
        assert data["_id"] == str(playlist_id)
    
    def test_get_playlist_not_found(self, client, mock_db):
        """בדיקת קבלת פלייליסט שלא קיים"""
        mock_db.db.playlists.find_one.return_value = None
        
        response = client.get(f'/api/playlists/{str(ObjectId())}')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Playlist not found" in data["error"]
    
    def test_delete_playlist_success(self, client, mock_db):
        """בדיקת מחיקת פלייליסט"""
        playlist_id = str(ObjectId())
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_db.db.playlists.delete_one.return_value = mock_result
        
        response = client.delete(f'/api/playlists/{playlist_id}')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        mock_db.db.playlists.delete_one.assert_called_once_with({"_id": ObjectId(playlist_id)})

    def test_get_playlists_db_error(self, client, mock_db):
        """בדיקת שגיאת דאטהבייס בקבלת פלייליסטים"""
        mock_db.db.playlists.find.side_effect = Exception("DB Error")
        
        response = client.get('/api/playlists')
        data = response.get_json()
        
        assert response.status_code == 500
        assert data["success"] is False
        assert "error" in data

    def test_get_playlist_db_error(self, client, mock_db):
        """בדיקת שגיאת דאטהבייס בקבלת פלייליסט בודד"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.side_effect = Exception("DB Error")
        
        response = client.get(f'/api/playlists/{playlist_id}')
        data = response.get_json()
        
        assert response.status_code == 500
        assert data["success"] is False
        assert "error" in data


class TestPlaylistSongs:
    def test_add_song_to_playlist_success(self, client, mock_db):
        """בדיקת הוספת שיר לפלייליסט"""
        playlist_id = str(ObjectId())
        mock_result = Mock()
        mock_result.matched_count = 1
        mock_db.db.playlists.update_one.return_value = mock_result
        
        song_data = {
            "artist_id": str(ObjectId()),
            "artist_name": "עידן רייכל",
            "title": "מילים",
            "duration": "4:20"
        }
        
        response = client.post(f'/api/playlists/{playlist_id}/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
        mock_db.db.playlists.update_one.assert_called_once()
    
    def test_add_song_to_playlist_missing_fields(self, client, mock_db):
        """בדיקת הוספת שיר עם שדות חסרים"""
        playlist_id = str(ObjectId())
        song_data = {
            "title": "מילים",
            "duration": "4:20"
        }
        
        response = client.post(f'/api/playlists/{playlist_id}/songs', json=song_data)
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False
        assert "required" in data["error"]
    
    def test_remove_song_from_playlist_success(self, client, mock_db):
        """בדיקת הסרת שיר מפלייליסט"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.return_value = {
            "_id": ObjectId(playlist_id),
            "name": "פלייליסט",
            "songs": [{"title": "שיר לדוגמה", "duration": "3:30"}]
        }
        
        response = client.delete(f'/api/playlists/{playlist_id}/songs/0')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data["success"] is True
    
    def test_remove_song_invalid_index(self, client, mock_db):
        """בדיקת הסרת שיר עם אינדקס לא תקין"""
        playlist_id = str(ObjectId())
        mock_db.db.playlists.find_one.return_value = {
            "_id": ObjectId(playlist_id),
            "name": "פלייליסט",
            "songs": []
        }
        
        response = client.delete(f'/api/playlists/{playlist_id}/songs/0')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data["success"] is False
        assert "Song index out of range" in data["error"]

    def test_add_song_invalid_json(self, client, mock_db):
        """בדיקת הוספת שיר עם JSON לא תקין"""
        playlist_id = str(ObjectId())
        
        response = client.post(f'/api/playlists/{playlist_id}/songs',
                            data="{invalid-json}",  # שינינו מ-"invalid json" ל-"{invalid-json}"
                            content_type='application/json')
        data = response.get_json()
        
        assert response.status_code == 400
        assert data["success"] is False