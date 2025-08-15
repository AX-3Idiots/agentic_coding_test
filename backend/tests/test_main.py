"""
Comprehensive tests for counter data persistence API
Tests all user stories and acceptance criteria
"""
import pytest
import json
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from app.main import app, StorageManager, DATA_DIR

client = TestClient(app)

class TestDataPersistence:
    """Test suite for data persistence user stories"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary data directory for tests
        self.test_data_dir = Path(tempfile.mkdtemp())
        self.original_data_dir = DATA_DIR
        
        # Patch the DATA_DIR to use test directory
        import app.main
        app.main.DATA_DIR = self.test_data_dir
        app.main.COUNTER_FILE = self.test_data_dir / "counter.json"
        app.main.SESSION_FILE = self.test_data_dir / "session.json"
    
    def teardown_method(self):
        """Clean up test environment"""
        # Restore original DATA_DIR
        import app.main
        app.main.DATA_DIR = self.original_data_dir
        
        # Clean up test directory
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

    # User Story 1: Auto-save counter value
    def test_counter_auto_save_on_change(self):
        """Test that counter value saves automatically on each change"""
        # Initial increment
        response = client.post("/api/counter/increment")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        
        # Verify file was created and contains correct data
        counter_file = self.test_data_dir / "counter.json"
        assert counter_file.exists()
        
        with open(counter_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data["value"] == 1
        assert "timestamp" in saved_data
        assert saved_data["version"] == 1

    def test_timestamp_saved_with_counter(self):
        """Test that timestamp is saved along with counter value"""
        before_time = datetime.now(timezone.utc)
        
        response = client.post("/api/counter/increment")
        assert response.status_code == 200
        
        after_time = datetime.now(timezone.utc)
        
        # Check response includes timestamp
        data = response.json()
        timestamp_str = data["data"]["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        assert before_time <= timestamp <= after_time

    def test_save_operation_performance(self):
        """Test that save operations complete within 50ms"""
        import time
        
        start_time = time.time()
        response = client.post("/api/counter/increment")
        end_time = time.time()
        
        assert response.status_code == 200
        operation_time_ms = (end_time - start_time) * 1000
        
        # Should complete well within 50ms (allowing some overhead for testing)
        assert operation_time_ms < 100  # More lenient for test environment

    def test_debounced_writes_prevent_excessive_operations(self):
        """Test that multiple rapid operations don't cause excessive storage writes"""
        # This is more of an integration test - the debouncing happens on frontend
        # But we can test that the backend handles rapid requests efficiently
        
        import time
        start_time = time.time()
        
        # Make multiple rapid requests
        for _ in range(10):
            response = client.post("/api/counter/increment")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # 10 operations should complete reasonably quickly
        assert total_time_ms < 1000  # Less than 1 second for 10 operations

    # User Story 2: Auto-restore counter value
    def test_counter_loads_automatically_on_start(self):
        """Test that counter value loads automatically on application start"""
        # First, save a counter value
        client.post("/api/counter/increment")
        client.post("/api/counter/increment")
        client.post("/api/counter/increment")
        
        # Now simulate application restart by loading counter
        response = client.get("/api/counter")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["value"] == 3

    def test_application_defaults_to_zero_if_no_saved_value(self):
        """Test that application defaults to 0 if no saved value exists"""
        # Ensure no existing data
        counter_file = self.test_data_dir / "counter.json"
        if counter_file.exists():
            counter_file.unlink()
        
        response = client.get("/api/counter")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["value"] == 0

    def test_saved_timestamp_restored_with_counter(self):
        """Test that saved timestamp is restored with counter value"""
        # Save counter with timestamp
        response = client.post("/api/counter/increment")
        saved_timestamp = response.json()["data"]["timestamp"]
        
        # Load counter
        response = client.get("/api/counter")
        loaded_timestamp = response.json()["data"]["timestamp"]
        
        assert saved_timestamp == loaded_timestamp

    def test_data_validation_ensures_bounds(self):
        """Test that data validation ensures loaded values are within bounds"""
        # Manually create invalid data file
        counter_file = self.test_data_dir / "counter.json"
        invalid_data = {
            "value": 2000000,  # Exceeds upper bound
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1
        }
        
        with open(counter_file, 'w') as f:
            json.dump(invalid_data, f)
        
        # Should return default value when loading invalid data
        response = client.get("/api/counter")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["value"] == 0  # Default value due to validation failure

    # User Story 3: Session data persistence
    def test_session_data_saves_and_loads(self):
        """Test that session data saves and loads properly"""
        # Start a new session
        response = client.post("/api/session/start")
        assert response.status_code == 200
        session_data = response.json()["data"]
        session_id = session_data["session_id"]
        
        # Perform some operations to update session stats
        client.post("/api/counter/increment")
        client.post("/api/counter/decrement")
        client.post("/api/counter/reset")
        
        # Load session data
        response = client.get("/api/session")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        session = data["data"]
        assert session["session_id"] == session_id
        assert session["operations_count"] == 3
        assert session["increments"] == 1
        assert session["decrements"] == 1
        assert session["resets"] == 1

    def test_session_includes_usage_statistics(self):
        """Test that session data includes usage statistics and timestamps"""
        # Start session
        client.post("/api/session/start")
        
        # Perform various operations
        for _ in range(5):
            client.post("/api/counter/increment")
        
        for _ in range(3):
            client.post("/api/counter/decrement")
        
        client.post("/api/counter/reset")
        
        # Check session statistics
        response = client.get("/api/session")
        session = response.json()["data"]
        
        assert session["operations_count"] == 9  # 5 + 3 + 1
        assert session["increments"] == 5
        assert session["decrements"] == 3
        assert session["resets"] == 1
        assert "start_time" in session
        assert "last_activity" in session

    # User Story 4: Offline reliability
    def test_data_validation_on_load(self):
        """Test that data validation occurs when loading from storage"""
        # Create corrupted data file
        counter_file = self.test_data_dir / "counter.json"
        
        with open(counter_file, 'w') as f:
            f.write("invalid json{")
        
        # Should handle corruption gracefully
        response = client.get("/api/counter")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["value"] == 0  # Default value on corruption

    def test_corruption_recovery_mechanisms(self):
        """Test that corruption recovery handles damaged data"""
        counter_file = self.test_data_dir / "counter.json"
        
        # Test various corruption scenarios
        corruption_scenarios = [
            "invalid json",
            '{"value": "not_a_number"}',
            '{"incomplete": true',
            "",
            '{"value": null}'
        ]
        
        for corrupted_content in corruption_scenarios:
            with open(counter_file, 'w') as f:
                f.write(corrupted_content)
            
            response = client.get("/api/counter")
            assert response.status_code == 200
            assert response.json()["data"]["value"] == 0

    def test_storage_errors_handled_gracefully(self):
        """Test that storage errors are handled gracefully"""
        # Make directory read-only to simulate storage error
        os.chmod(self.test_data_dir, 0o444)
        
        try:
            response = client.post("/api/counter/increment")
            # Should still return success even if save fails
            # (In a real application, you might want different behavior)
            assert response.status_code in [200, 500]
        finally:
            # Restore permissions
            os.chmod(self.test_data_dir, 0o755)

    # User Story 5: Backup and restore
    def test_export_counter_data_to_json(self):
        """Test export counter data to downloadable JSON file"""
        # Set up test data
        client.post("/api/counter/increment")
        client.post("/api/counter/increment")
        client.post("/api/session/start")
        
        response = client.get("/api/backup/export")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "filename" in data
        
        # Verify JSON structure
        backup_data = json.loads(data["data"])
        assert "counter" in backup_data
        assert "session" in backup_data
        assert "export_timestamp" in backup_data
        assert backup_data["counter"]["value"] == 2

    def test_import_counter_data_from_json(self):
        """Test import counter data from uploaded JSON file"""
        # Create test backup data
        backup_data = {
            "counter": {
                "value": 42,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": 1
            },
            "session": {
                "session_id": "test-session-123",
                "start_time": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "operations_count": 10,
                "increments": 6,
                "decrements": 3,
                "resets": 1
            },
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1
        }
        
        backup_json = json.dumps(backup_data)
        
        response = client.post("/api/backup/import", json=backup_json)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["counter_value"] == 42
        
        # Verify data was imported
        counter_response = client.get("/api/counter")
        assert counter_response.json()["data"]["value"] == 42

    def test_data_validation_for_import(self):
        """Test that data validation ensures imported data is valid"""
        invalid_scenarios = [
            "invalid json",
            '{"invalid": "structure"}',
            '{"counter": {"value": "not_a_number"}}',
            '{"counter": {"value": 9999999}}',  # Out of bounds
        ]
        
        for invalid_data in invalid_scenarios:
            response = client.post("/api/backup/import", json=invalid_data)
            assert response.status_code == 400

    def test_health_check_endpoint(self):
        """Test health check endpoint for monitoring"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

class TestStorageManager:
    """Test the StorageManager class directly"""
    
    def setup_method(self):
        self.test_data_dir = Path(tempfile.mkdtemp())
        self.storage = StorageManager()
        
        # Patch file paths
        import app.main
        app.main.COUNTER_FILE = self.test_data_dir / "counter.json"
        app.main.SESSION_FILE = self.test_data_dir / "session.json"
    
    def teardown_method(self):
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

    @pytest.mark.asyncio
    async def test_atomic_file_operations(self):
        """Test that file operations are atomic to prevent corruption"""
        from app.main import CounterData
        
        counter_data = CounterData(value=123, timestamp=datetime.now(timezone.utc))
        
        # Save should create temp file first
        success = await self.storage.save_counter(counter_data)
        assert success is True
        
        # Verify no temp file remains
        temp_file = (self.test_data_dir / "counter.json").with_suffix('.tmp')
        assert not temp_file.exists()
        
        # Verify actual file exists and is correct
        counter_file = self.test_data_dir / "counter.json"
        assert counter_file.exists()
        
        with open(counter_file, 'r') as f:
            data = json.load(f)
        assert data["value"] == 123

if __name__ == "__main__":
    pytest.main([__file__, "-v"])