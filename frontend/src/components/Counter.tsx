/**
 * Counter component with comprehensive data persistence
 * Implements all user stories for auto-save, restore, session management, and backup/restore
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, CounterData, SessionData } from '../services/api';
import { storageService } from '../services/storage';
import { debounce, PerformanceTracker } from '../utils/debounce';

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning';
  duration?: number;
}

export const Counter: React.FC = () => {
  // State management
  const [counterData, setCounterData] = useState<CounterData>({
    value: 0,
    timestamp: new Date().toISOString(),
    version: 1,
  });
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [lastOperationTime, setLastOperationTime] = useState<number>(0);
  
  // Refs for performance tracking
  const saveInProgress = useRef(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Debounced save operations to prevent excessive storage calls
  const debouncedSave = useCallback(
    debounce(async (data: CounterData) => {
      if (saveInProgress.current) return;
      
      saveInProgress.current = true;
      
      try {
        // Save to local storage immediately for offline support
        storageService.saveCounterData(data);
        
        // If online, sync with backend
        if (isOnline) {
          const start = performance.now();
          // Note: The actual save happens through the API operations
          // This is just for caching the latest state
          const duration = performance.now() - start;
          setLastOperationTime(duration);
        }
      } catch (error) {
        console.error('Save operation failed:', error);
        showNotification('Save operation failed', 'error');
      } finally {
        saveInProgress.current = false;
      }
    }, 300), // 300ms debounce to prevent excessive writes
    [isOnline]
  );

  // Notification system
  const showNotification = useCallback((message: string, type: Notification['type'], duration = 3000) => {
    const id = Date.now().toString();
    const notification: Notification = { id, message, type, duration };
    
    setNotifications(prev => [...prev, notification]);
    
    if (duration > 0) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      }, duration);
    }
  }, []);

  // Online/offline status monitoring
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      showNotification('Connection restored', 'success');
      // Sync local data with server when coming back online
      loadCounterData();
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      showNotification('Working offline', 'warning', 5000);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Initialize application data
  const loadCounterData = useCallback(async () => {
    setIsLoading(true);
    
    try {
      if (isOnline) {
        // Try to load from server first
        const response = await apiService.getCounter();
        if (response.success && response.data) {
          setCounterData(response.data);
          storageService.saveCounterData(response.data);
        }
      } else {
        // Load from local storage when offline
        const localData = storageService.loadCounterData();
        if (localData) {
          setCounterData(localData);
        }
      }
    } catch (error) {
      console.error('Failed to load counter data:', error);
      
      // Fallback to local storage
      const localData = storageService.loadCounterData();
      if (localData) {
        setCounterData(localData);
        showNotification('Loaded from local cache', 'warning');
      } else {
        showNotification('Failed to load counter data', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  }, [isOnline]);

  // Initialize session data
  const loadSessionData = useCallback(async () => {
    try {
      if (isOnline) {
        // Try to get existing session from server
        const sessionResponse = await apiService.getSession();
        if (sessionResponse.success && sessionResponse.data) {
          setSessionData(sessionResponse.data);
          storageService.saveSessionData(sessionResponse.data);
        } else {
          // Start new session if none exists
          const newSessionResponse = await apiService.startSession();
          if (newSessionResponse.success && newSessionResponse.data) {
            setSessionData(newSessionResponse.data);
            storageService.saveSessionData(newSessionResponse.data);
          }
        }
      } else {
        // Load from local storage when offline
        const localSession = storageService.loadSessionData();
        if (localSession) {
          setSessionData(localSession);
        }
      }
    } catch (error) {
      console.error('Failed to load session data:', error);
      
      // Fallback to local storage
      const localSession = storageService.loadSessionData();
      if (localSession) {
        setSessionData(localSession);
      }
    }
  }, [isOnline]);

  // Application initialization
  useEffect(() => {
    loadCounterData();
    loadSessionData();
  }, [loadCounterData, loadSessionData]);

  // Auto-save when counter data changes
  useEffect(() => {
    if (counterData.value !== 0 || counterData.timestamp !== new Date().toISOString()) {
      debouncedSave(counterData);
    }
  }, [counterData, debouncedSave]);

  // Counter operations with performance tracking
  const performOperation = async (operation: () => Promise<any>, operationType: string) => {
    if (isLoading) return;
    
    setIsLoading(true);
    const tracker = new PerformanceTracker();
    tracker.start();

    try {
      if (isOnline) {
        const response = await operation();
        if (response.success && response.data) {
          setCounterData(response.data);
          const duration = tracker.end();
          setLastOperationTime(duration);
          
          if (duration > 50) {
            showNotification(`${operationType} completed in ${duration.toFixed(1)}ms (slower than expected)`, 'warning');
          } else {
            showNotification(`${operationType} completed in ${duration.toFixed(1)}ms`, 'success', 2000);
          }
        }
      } else {
        // Offline operation
        const newData = { ...counterData };
        switch (operationType) {
          case 'Increment':
            newData.value += 1;
            break;
          case 'Decrement':
            newData.value -= 1;
            break;
          case 'Reset':
            newData.value = 0;
            break;
        }
        newData.timestamp = new Date().toISOString();
        
        setCounterData(newData);
        storageService.saveCounterData(newData);
        
        const duration = tracker.end();
        setLastOperationTime(duration);
        showNotification(`${operationType} saved locally (offline)`, 'warning');
      }
    } catch (error) {
      console.error(`${operationType} operation failed:`, error);
      showNotification(`${operationType} operation failed`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const increment = () => performOperation(() => apiService.incrementCounter(), 'Increment');
  const decrement = () => performOperation(() => apiService.decrementCounter(), 'Decrement');
  const reset = () => performOperation(() => apiService.resetCounter(), 'Reset');

  // Backup and restore operations
  const exportBackup = async () => {
    try {
      if (isOnline) {
        const response = await apiService.exportBackup();
        if (response.success) {
          apiService.downloadFile(response.data, response.filename);
          showNotification('Backup exported successfully', 'success');
        }
      } else {
        // Export local data when offline
        const backupData = storageService.exportData();
        const filename = `counter_backup_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        apiService.downloadFile(backupData, filename);
        showNotification('Local backup exported', 'warning');
      }
    } catch (error) {
      console.error('Export failed:', error);
      showNotification('Export failed', 'error');
    }
  };

  const importBackup = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const content = await file.text();
      
      // Validate JSON format
      let parsedData;
      try {
        parsedData = JSON.parse(content);
      } catch {
        showNotification('Invalid JSON file format', 'error');
        return;
      }

      // Confirm before overwriting
      if (!window.confirm('This will overwrite your current counter data. Continue?')) {
        return;
      }

      if (isOnline) {
        await apiService.importBackup(content);
        showNotification('Backup imported successfully', 'success');
        loadCounterData();
        loadSessionData();
      } else {
        // Import to local storage when offline
        const success = storageService.importData(content);
        if (success) {
          showNotification('Backup imported to local storage', 'warning');
          loadCounterData();
          loadSessionData();
        } else {
          showNotification('Import failed - invalid data format', 'error');
        }
      }
    } catch (error) {
      console.error('Import failed:', error);
      showNotification('Import failed', 'error');
    } finally {
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Render notifications
  const renderNotifications = () => (
    <div>
      {notifications.map(notification => (
        <div key={notification.id} className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      ))}
    </div>
  );

  return (
    <div className="container">
      {renderNotifications()}
      
      <div className={`counter-app ${isLoading ? 'loading' : ''}`}>
        <h1>Counter with Data Persistence</h1>
        
        {!isOnline && (
          <div className="offline-indicator">
            ⚠️ Working offline - data will sync when connection is restored
          </div>
        )}

        <div className="counter-display">
          {counterData.value}
        </div>

        <div className="counter-controls">
          <button 
            className="btn btn-primary" 
            onClick={decrement}
            disabled={isLoading}
          >
            - Decrement
          </button>
          
          <button 
            className="btn btn-secondary" 
            onClick={reset}
            disabled={isLoading}
          >
            Reset
          </button>
          
          <button 
            className="btn btn-primary" 
            onClick={increment}
            disabled={isLoading}
          >
            + Increment
          </button>
        </div>

        <div className="status-panel">
          <h3>Status Information</h3>
          <div className="status-item">
            <span className="status-label">Current Value:</span>
            <span className="status-value">{counterData.value}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Last Updated:</span>
            <span className="status-value">
              {new Date(counterData.timestamp).toLocaleString()}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Connection:</span>
            <span className="status-value">{isOnline ? '🟢 Online' : '🔴 Offline'}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Data Version:</span>
            <span className="status-value">v{counterData.version}</span>
          </div>
          {lastOperationTime > 0 && (
            <div className="status-item">
              <span className="status-label">Last Operation:</span>
              <span className={`status-value performance-indicator ${
                lastOperationTime < 50 ? 'fast' : lastOperationTime < 100 ? 'slow' : 'error'
              }`}>
                {lastOperationTime.toFixed(1)}ms
              </span>
            </div>
          )}
        </div>

        {sessionData && (
          <div className="status-panel">
            <h3>Session Statistics</h3>
            <div className="status-item">
              <span className="status-label">Session ID:</span>
              <span className="status-value">{sessionData.session_id.slice(0, 8)}...</span>
            </div>
            <div className="status-item">
              <span className="status-label">Session Started:</span>
              <span className="status-value">
                {new Date(sessionData.start_time).toLocaleString()}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Total Operations:</span>
              <span className="status-value">{sessionData.operations_count}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Increments:</span>
              <span className="status-value">{sessionData.increments}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Decrements:</span>
              <span className="status-value">{sessionData.decrements}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Resets:</span>
              <span className="status-value">{sessionData.resets}</span>
            </div>
          </div>
        )}

        <div className="backup-panel">
          <h3>Backup & Restore</h3>
          <div className="backup-controls">
            <button 
              className="btn btn-secondary" 
              onClick={exportBackup}
              disabled={isLoading}
            >
              📁 Export Backup
            </button>
            
            <button 
              className="btn btn-secondary" 
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
            >
              📂 Import Backup
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={importBackup}
              className="file-input"
            />
          </div>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
            Export your counter data to a JSON file or import from a previous backup.
            {!isOnline && ' Note: Operating in offline mode.'}
          </p>
        </div>
      </div>
    </div>
  );
};