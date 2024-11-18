import pytest
import requests
import os
from pymongo import MongoClient
from bson import ObjectId

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:5000")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/test_music_db")

@pytest.fixture
def client():
    return requests

@pytest.fixture
def mock_db():
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    db.artists.delete_many({})
    db.playlists.delete_many({})
    db.favorites.delete_many({})
    yield db
    db.artists.delete_many({})
    db.playlists.delete_many({})
    db.favorites.delete_many({})

# Artist Tests
def test_get_artists_empty(client, mock_db):
    response = client.get(f"{BACKEND_URL}/api/artists")
    assert response.status_code == 200
    assert response.json() == []

def test_get_artists(client, mock_db):
    artist = {"name": "Test Artist", "songs": []}
    result = mock_db.artists.insert_one(artist)
    
    response = client.get(f"{BACKEND_URL}/api/artists")
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == 'Test Artist'
    assert data[0]['_id'] == str(result.inserted_id)

def test_add_artist_success(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/artists", json={'name': 'New Artist'})
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True
    assert 'id' in data

def test_add_artist_empty_name(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/artists", json={'name': ''})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False
    assert 'error' in data

def test_add_artist_missing_name(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/artists", json={})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False
    assert 'error' in data

def test_delete_artist_success(client, mock_db):
    result = mock_db.artists.insert_one({'name': 'Delete Me', 'songs': []})
    artist_id = str(result.inserted_id)
    
    response = client.delete(f"{BACKEND_URL}/api/artists/{artist_id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True
    assert mock_db.artists.find_one({'_id': ObjectId(artist_id)}) is None

def test_delete_artist_not_found(client, mock_db):
    response = client.delete(f"{BACKEND_URL}/api/artists/{str(ObjectId())}")
    data = response.json()
    
    assert response.status_code == 404
    assert data['success'] is False

def test_delete_artist_invalid_id(client, mock_db):
    response = client.delete(f"{BACKEND_URL}/api/artists/invalid-id")
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False

# Song Tests
def test_add_song_success(client, mock_db):
    result = mock_db.artists.insert_one({'name': 'Artist', 'songs': []})
    artist_id = str(result.inserted_id)
    
    response = client.post(f"{BACKEND_URL}/api/artists/{artist_id}/songs", 
                         json={'title': 'Test Song', 'duration': '3:30'})
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True

def test_add_song_missing_fields(client, mock_db):
    result = mock_db.artists.insert_one({'name': 'Artist', 'songs': []})
    artist_id = str(result.inserted_id)
    
    response = client.post(f"{BACKEND_URL}/api/artists/{artist_id}/songs", json={'title': 'Test Song'})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False

def test_add_song_artist_not_found(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/artists/{str(ObjectId())}/songs", 
                         json={'title': 'Test Song', 'duration': '3:30'})
    data = response.json()
    
    assert response.status_code == 404
    assert data['success'] is False

def test_delete_song_success(client, mock_db):
    artist = {
        'name': 'Artist',
        'songs': [{'title': 'Delete This', 'duration': '4:00'}]
    }
    result = mock_db.artists.insert_one(artist)
    artist_id = str(result.inserted_id)
    
    response = client.delete(f"{BACKEND_URL}/api/artists/{artist_id}/songs/0")
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True

def test_delete_song_invalid_index(client, mock_db):
    result = mock_db.artists.insert_one({'name': 'Artist', 'songs': []})
    artist_id = str(result.inserted_id)
    
    response = client.delete(f"{BACKEND_URL}/api/artists/{artist_id}/songs/0")
    data = response.json()
    
    assert response.status_code == 404
    assert data['success'] is False

# Playlist Tests
def test_get_playlists_empty(client, mock_db):
    response = client.get(f"{BACKEND_URL}/api/playlists")
    assert response.status_code == 200
    assert response.json() == []

def test_create_playlist_success(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/playlists", 
                         json={'name': 'My Playlist', 'description': 'Test playlist'})
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True
    assert 'id' in data

def test_create_playlist_empty_name(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/playlists", 
                         json={'name': '', 'description': 'Test playlist'})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False

def test_get_playlist_success(client, mock_db):
    result = mock_db.playlists.insert_one({'name': 'Test Playlist', 'songs': []})
    playlist_id = str(result.inserted_id)
    
    response = client.get(f"{BACKEND_URL}/api/playlists/{playlist_id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == 'Test Playlist'

def test_get_playlist_not_found(client, mock_db):
    response = client.get(f"{BACKEND_URL}/api/playlists/{str(ObjectId())}")
    data = response.json()
    
    assert response.status_code == 404
    assert data['success'] is False

def test_add_song_to_playlist_success(client, mock_db):
    result = mock_db.playlists.insert_one({'name': 'Test Playlist', 'songs': []})
    playlist_id = str(result.inserted_id)
    
    song_data = {
        'artist_id': str(ObjectId()),
        'artist_name': 'Test Artist',
        'title': 'Test Song',
        'duration': '3:30'
    }
    
    response = client.post(f"{BACKEND_URL}/api/playlists/{playlist_id}/songs", json=song_data)
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True

def test_add_song_to_playlist_missing_fields(client, mock_db):
    result = mock_db.playlists.insert_one({'name': 'Test Playlist', 'songs': []})
    playlist_id = str(result.inserted_id)
    
    response = client.post(f"{BACKEND_URL}/api/playlists/{playlist_id}/songs", 
                         json={'title': 'Test Song'})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False

# Favorites Tests
def test_get_favorites_empty(client, mock_db):
    response = client.get(f"{BACKEND_URL}/api/favorites")
    data = response.json()
    
    assert response.status_code == 200
    assert 'songs' in data
    assert len(data['songs']) == 0

def test_add_favorite_song_success(client, mock_db):
    song_data = {
        'artist_id': str(ObjectId()),
        'artist_name': 'Test Artist',
        'title': 'Test Song',
        'duration': '3:30'
    }
    
    response = client.post(f"{BACKEND_URL}/api/favorites/songs", json=song_data)
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True

def test_add_favorite_song_missing_fields(client, mock_db):
    response = client.post(f"{BACKEND_URL}/api/favorites/songs", 
                         json={'title': 'Test Song'})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False

def test_remove_favorite_song_success(client, mock_db):
    song_data = {
        'artist_id': '123',
        'artist_name': 'Test Artist',
        'title': 'Test Song',
        'duration': '3:30'
    }
    mock_db.favorites.insert_one({
        'type': 'user_favorites',
        'songs': [song_data]
    })
    
    response = client.delete(f"{BACKEND_URL}/api/favorites/songs/123/Test%20Song")
    data = response.json()
    
    assert response.status_code == 200
    assert data['success'] is True

def test_add_song_to_playlist_empty_title(client, mock_db):
    result = mock_db.playlists.insert_one({'name': 'Test Playlist', 'songs': []})
    playlist_id = str(result.inserted_id)
    
    response = client.post(f"{BACKEND_URL}/api/playlists/{playlist_id}/songs", 
                         json={'title': '', 'artist_name': 'Test Artist', 
                              'artist_id': '123', 'duration': '3:30'})
    data = response.json()
    
    assert response.status_code == 400
    assert data['success'] is False
    assert 'error' in data