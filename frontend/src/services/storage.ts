/**
 * Local storage service for offline functionality and caching
 * Provides data validation, corruption recovery, and schema migration
 */

import { CounterData, SessionData } from './api';

const STORAGE_KEYS = {
  COUNTER: 'counter_data',
  SESSION: 'session_data',
  CACHE_TIMESTAMP: 'cache_timestamp',
  VERSION: 'storage_version',
} as const;

const CURRENT_VERSION = 1;
const CACHE_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

export interface StoredCounterData extends CounterData {
  cached_at: string;
}

export interface StoredSessionData extends SessionData {
  cached_at: string;
}

class LocalStorageService {
  constructor() {
    this.migrateStorageIfNeeded();
    this.cleanupExpiredData();
  }

  // Counter data operations
  saveCounterData(data: CounterData): boolean {
    try {
      const storedData: StoredCounterData = {
        ...data,
        cached_at: new Date().toISOString(),
      };
      
      localStorage.setItem(STORAGE_KEYS.COUNTER, JSON.stringify(storedData));
      localStorage.setItem(STORAGE_KEYS.CACHE_TIMESTAMP, new Date().toISOString());
      return true;
    } catch (error) {
      console.error('Failed to save counter data to localStorage:', error);
      return false;
    }
  }

  loadCounterData(): CounterData | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.COUNTER);
      if (!stored) return null;

      const data = JSON.parse(stored) as StoredCounterData;
      
      // Validate data structure
      if (!this.isValidCounterData(data)) {
        console.warn('Invalid counter data in localStorage, clearing...');
        this.clearCounterData();
        return null;
      }

      // Check if data is expired
      if (this.isDataExpired(data.cached_at)) {
        console.info('Cached counter data expired, clearing...');
        this.clearCounterData();
        return null;
      }

      return {
        value: data.value,
        timestamp: data.timestamp,
        version: data.version,
      };
    } catch (error) {
      console.error('Failed to load counter data from localStorage:', error);
      this.clearCounterData();
      return null;
    }
  }

  clearCounterData(): void {
    localStorage.removeItem(STORAGE_KEYS.COUNTER);
  }

  // Session data operations
  saveSessionData(data: SessionData): boolean {
    try {
      const storedData: StoredSessionData = {
        ...data,
        cached_at: new Date().toISOString(),
      };
      
      localStorage.setItem(STORAGE_KEYS.SESSION, JSON.stringify(storedData));
      return true;
    } catch (error) {
      console.error('Failed to save session data to localStorage:', error);
      return false;
    }
  }

  loadSessionData(): SessionData | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.SESSION);
      if (!stored) return null;

      const data = JSON.parse(stored) as StoredSessionData;
      
      // Validate data structure
      if (!this.isValidSessionData(data)) {
        console.warn('Invalid session data in localStorage, clearing...');
        this.clearSessionData();
        return null;
      }

      // Don't expire session data - it should persist across sessions
      return {
        session_id: data.session_id,
        start_time: data.start_time,
        last_activity: data.last_activity,
        operations_count: data.operations_count,
        increments: data.increments,
        decrements: data.decrements,
        resets: data.resets,
      };
    } catch (error) {
      console.error('Failed to load session data from localStorage:', error);
      this.clearSessionData();
      return null;
    }
  }

  clearSessionData(): void {
    localStorage.removeItem(STORAGE_KEYS.SESSION);
  }

  // Validation helpers
  private isValidCounterData(data: any): data is StoredCounterData {
    return (
      typeof data === 'object' &&
      data !== null &&
      typeof data.value === 'number' &&
      typeof data.timestamp === 'string' &&
      typeof data.version === 'number' &&
      typeof data.cached_at === 'string' &&
      data.value >= -1000000 &&
      data.value <= 1000000
    );
  }

  private isValidSessionData(data: any): data is StoredSessionData {
    return (
      typeof data === 'object' &&
      data !== null &&
      typeof data.session_id === 'string' &&
      typeof data.start_time === 'string' &&
      typeof data.last_activity === 'string' &&
      typeof data.operations_count === 'number' &&
      typeof data.increments === 'number' &&
      typeof data.decrements === 'number' &&
      typeof data.resets === 'number' &&
      typeof data.cached_at === 'string'
    );
  }

  private isDataExpired(cachedAt: string): boolean {
    try {
      const cacheTime = new Date(cachedAt).getTime();
      const now = Date.now();
      return (now - cacheTime) > CACHE_EXPIRY_MS;
    } catch {
      return true; // Treat invalid dates as expired
    }
  }

  // Storage management
  private migrateStorageIfNeeded(): void {
    try {
      const currentVersion = parseInt(localStorage.getItem(STORAGE_KEYS.VERSION) || '0', 10);
      
      if (currentVersion < CURRENT_VERSION) {
        console.info(`Migrating storage from version ${currentVersion} to ${CURRENT_VERSION}`);
        
        // Perform migration logic here if needed
        switch (currentVersion) {
          case 0:
            // Initial version - no migration needed
            break;
          default:
            console.warn('Unknown storage version, clearing all data');
            this.clearAllData();
        }
        
        localStorage.setItem(STORAGE_KEYS.VERSION, CURRENT_VERSION.toString());
      }
    } catch (error) {
      console.error('Storage migration failed:', error);
      this.clearAllData();
    }
  }

  private cleanupExpiredData(): void {
    try {
      const cacheTimestamp = localStorage.getItem(STORAGE_KEYS.CACHE_TIMESTAMP);
      if (cacheTimestamp && this.isDataExpired(cacheTimestamp)) {
        console.info('Cleaning up expired cache data');
        this.clearCounterData();
      }
    } catch (error) {
      console.error('Cache cleanup failed:', error);
    }
  }

  clearAllData(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  }

  // Utility methods
  getStorageInfo(): {
    hasCounterData: boolean;
    hasSessionData: boolean;
    cacheAge: number | null;
    storageVersion: number;
  } {
    const hasCounterData = localStorage.getItem(STORAGE_KEYS.COUNTER) !== null;
    const hasSessionData = localStorage.getItem(STORAGE_KEYS.SESSION) !== null;
    const storageVersion = parseInt(localStorage.getItem(STORAGE_KEYS.VERSION) || '0', 10);
    
    let cacheAge: number | null = null;
    const cacheTimestamp = localStorage.getItem(STORAGE_KEYS.CACHE_TIMESTAMP);
    if (cacheTimestamp) {
      try {
        cacheAge = Date.now() - new Date(cacheTimestamp).getTime();
      } catch {
        cacheAge = null;
      }
    }

    return {
      hasCounterData,
      hasSessionData,
      cacheAge,
      storageVersion,
    };
  }

  // Export/Import for backup functionality
  exportData(): string {
    const counterData = this.loadCounterData();
    const sessionData = this.loadSessionData();
    
    return JSON.stringify({
      counter: counterData,
      session: sessionData,
      export_timestamp: new Date().toISOString(),
      version: CURRENT_VERSION,
    }, null, 2);
  }

  importData(jsonString: string): boolean {
    try {
      const data = JSON.parse(jsonString);
      
      if (data.counter && this.isValidCounterData({ ...data.counter, cached_at: new Date().toISOString() })) {
        this.saveCounterData(data.counter);
      }
      
      if (data.session && this.isValidSessionData({ ...data.session, cached_at: new Date().toISOString() })) {
        this.saveSessionData(data.session);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  }
}

export const storageService = new LocalStorageService();