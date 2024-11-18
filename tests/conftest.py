import pytest
from unittest.mock import Mock, patch
from app import app

@pytest.fixture
def client():
    """יצירת client לבדיקות"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """יצירת mock לדאטהבייס"""
    with patch('app.mongo') as mock_mongo:
        # הגדרת mock collection לאמנים
        mock_artists_collection = Mock()
        mock_mongo.db.artists = mock_artists_collection
        
        # הגדרת mock collection לפלייליסטים
        mock_playlists_collection = Mock()
        mock_mongo.db.playlists = mock_playlists_collection
        
        # הגדרת mock collection למועדפים
        mock_favorites_collection = Mock()
        mock_mongo.db.favorites = mock_favorites_collection
        
        yield mock_mongo