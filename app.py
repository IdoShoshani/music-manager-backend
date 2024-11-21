from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId, errors
import os
from dotenv import load_dotenv
from functools import wraps
import json

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://mongo:27017/music_db")
mongo = PyMongo(app)


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health Check endpoint for MongoDB connection.

    This endpoint verifies the connectivity to the MongoDB instance by sending
    a simple 'ping' command. It returns the health status of the backend
    and the database connection.

    Returns:
        200 OK: If MongoDB connection is successful.
        401 Unauthorized: If there is an authentication error.
        500 Internal Server Error: For other types of errors (e.g., MongoDB unavailable).
    """
    try:
        # Ping the MongoDB server to check connectivity
        mongo.cx.admin.command("ping")
        return jsonify({"success": True, "status": "healthy", "database": "connected"}), 200
    except Exception as e:
        # Handle errors, including authentication issues
        error_message = str(e)
        if "Authentication failed" in error_message:
            # Return 401 if there is an authentication issue
            return jsonify({"success": False, "status": "unhealthy", "error": "Authentication failed"}), 401
        
        # Return 500 for any other errors
        return jsonify({"success": False, "status": "unhealthy", "error": error_message}), 500

def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
        # נסיון לפרסר את ה-JSON והחזרת שגיאה מתאימה אם נכשל
        try:
            # בדיקה מוקדמת של ה-JSON
            request.get_json(force=True)
        except Exception:
            return jsonify({"success": False, "error": "Invalid JSON format"}), 400
            
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/artists", methods=["GET"])
def get_artists():
    try:
        artists = list(mongo.db.artists.find())
        for artist in artists:
            artist["_id"] = str(artist["_id"])
        return jsonify(artists)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/artists", methods=["POST"])
@validate_json
def add_artist():
    try:
        name = request.json.get("name")
        if not name or len(name.strip()) == 0:
            return jsonify({"success": False, "error": "Artist name is required"}), 400

        result = mongo.db.artists.insert_one({"name": name, "songs": []})
        return jsonify({
            "success": True,
            "id": str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    try:
        result = mongo.db.artists.delete_one({"_id": ObjectId(artist_id)})
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Artist not found"}), 404
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid artist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/artists/<artist_id>/songs", methods=["POST"])
@validate_json
def add_song(artist_id):
    try:
        title = request.json.get("title")
        duration = request.json.get("duration")

        if not title or not duration:
            return jsonify({"success": False, "error": "Title and duration are required"}), 400

        song = {"title": title, "duration": duration}
        result = mongo.db.artists.update_one(
            {"_id": ObjectId(artist_id)},
            {"$push": {"songs": song}}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Artist not found"}), 404
            
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid artist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/artists/<artist_id>/songs/<int:song_index>", methods=["DELETE"])
def delete_song(artist_id, song_index):
    try:
        artist = mongo.db.artists.find_one({"_id": ObjectId(artist_id)})
        if not artist:
            return jsonify({"success": False, "error": "Artist not found"}), 404
            
        if song_index >= len(artist['songs']):
            return jsonify({"success": False, "error": "Song index out of range"}), 404

        mongo.db.artists.update_one(
            {"_id": ObjectId(artist_id)},
            {"$unset": {f"songs.{song_index}": 1}}
        )
        mongo.db.artists.update_one(
            {"_id": ObjectId(artist_id)},
            {"$pull": {"songs": None}}
        )
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid artist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Playlist Routes
@app.route("/api/playlists", methods=["GET"])
def get_playlists():
    try:
        playlists = list(mongo.db.playlists.find())
        for playlist in playlists:
            playlist["_id"] = str(playlist["_id"])
        return jsonify(playlists)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/playlists", methods=["POST"])
@validate_json
def create_playlist():
    try:
        name = request.json.get("name")
        if not name or len(name.strip()) == 0:
            return jsonify({"success": False, "error": "Playlist name is required"}), 400

        playlist_data = {
            "name": name,
            "description": request.json.get("description", ""),
            "songs": []
        }
        result = mongo.db.playlists.insert_one(playlist_data)
        return jsonify({
            "success": True,
            "id": str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/playlists/<playlist_id>", methods=["GET"])
def get_playlist(playlist_id):
    try:
        playlist = mongo.db.playlists.find_one({"_id": ObjectId(playlist_id)})
        if not playlist:
            return jsonify({"success": False, "error": "Playlist not found"}), 404
        playlist["_id"] = str(playlist["_id"])
        return jsonify(playlist)
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid playlist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/playlists/<playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id):
    try:
        result = mongo.db.playlists.delete_one({"_id": ObjectId(playlist_id)})
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Playlist not found"}), 404
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid playlist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/playlists/<playlist_id>/songs", methods=["POST"])
@validate_json
def add_song_to_playlist(playlist_id):
    try:
        required_fields = ["artist_id", "artist_name", "title", "duration"]
        for field in required_fields:
            if not request.json.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        song_data = {
            "artist_id": request.json["artist_id"],
            "artist_name": request.json["artist_name"],
            "title": request.json["title"],
            "duration": request.json["duration"]
        }

        result = mongo.db.playlists.update_one(
            {"_id": ObjectId(playlist_id)},
            {"$push": {"songs": song_data}}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Playlist not found"}), 404
            
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid playlist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/playlists/<playlist_id>/songs/<int:song_index>", methods=["DELETE"])
def remove_song_from_playlist(playlist_id, song_index):
    try:
        playlist = mongo.db.playlists.find_one({"_id": ObjectId(playlist_id)})
        if not playlist:
            return jsonify({"success": False, "error": "Playlist not found"}), 404

        if song_index >= len(playlist['songs']):
            return jsonify({"success": False, "error": "Song index out of range"}), 404

        mongo.db.playlists.update_one(
            {"_id": ObjectId(playlist_id)},
            {"$unset": {f"songs.{song_index}": 1}}
        )
        mongo.db.playlists.update_one(
            {"_id": ObjectId(playlist_id)},
            {"$pull": {"songs": None}}
        )
        return jsonify({"success": True})
    except errors.InvalidId:
        return jsonify({"success": False, "error": "Invalid playlist ID format"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Favorites Routes
@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    try:
        favorites = mongo.db.favorites.find_one({"type": "user_favorites"}) or {"songs": []}
        if "_id" in favorites:
            favorites["_id"] = str(favorites["_id"])
        return jsonify(favorites)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/favorites/songs", methods=["POST"])
@validate_json
def add_favorite_song():
    try:
        required_fields = ["artist_id", "artist_name", "title", "duration"]
        for field in required_fields:
            if not request.json.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        song_data = {
            "artist_id": request.json["artist_id"],
            "artist_name": request.json["artist_name"],
            "title": request.json["title"],
            "duration": request.json["duration"]
        }
        
        # Initialize favorites document if it doesn't exist
        mongo.db.favorites.update_one(
            {"type": "user_favorites"},
            {
                "$setOnInsert": {"type": "user_favorites", "songs": []},
            },
            upsert=True
        )
        
        # Add the song to favorites if it's not already there
        result = mongo.db.favorites.update_one(
            {
                "type": "user_favorites",
                "songs": {"$not": {"$elemMatch": {
                    "artist_id": song_data["artist_id"],
                    "title": song_data["title"]
                }}}
            },
            {"$push": {"songs": song_data}}
        )
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/favorites/songs/<artist_id>/<path:title>", methods=["DELETE"])
def remove_favorite_song(artist_id, title):
    try:
        result = mongo.db.favorites.update_one(
            {"type": "user_favorites"},
            {"$pull": {"songs": {"artist_id": artist_id, "title": title}}}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Favorites not found"}), 404
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)