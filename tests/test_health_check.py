def test_health_check_success(client, mock_db):
    """
    Test the health check endpoint when MongoDB is connected and healthy.
    """
    # Mock a successful ping to MongoDB
    mock_db.cx.admin.command.return_value = {"ok": 1}

    # Send GET request to /health endpoint
    response = client.get("/health")

    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json == {
        "success": True,
        "status": "healthy",
        "database": "connected"
    }


def test_health_check_authentication_failed(client, mock_db):
    """
    Test the health check endpoint when authentication to MongoDB fails.
    """
    # Mock an authentication failure
    mock_db.cx.admin.command.side_effect = Exception("Authentication failed")

    # Send GET request to /health endpoint
    response = client.get("/health")

    # Assert the response status code and content
    assert response.status_code == 401
    assert response.json == {
        "success": False,
        "status": "unhealthy",
        "error": "Authentication failed"
    }


def test_health_check_server_unavailable(client, mock_db):
    """
    Test the health check endpoint when MongoDB is unavailable.
    """
    # Mock a server unavailability error
    mock_db.cx.admin.command.side_effect = Exception("ServerSelectionTimeoutError: No servers found")

    # Send GET request to /health endpoint
    response = client.get("/health")

    # Assert the response status code and content
    assert response.status_code == 500
    assert response.json == {
        "success": False,
        "status": "unhealthy",
        "error": "ServerSelectionTimeoutError: No servers found"
    }
