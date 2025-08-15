/**
 * API service for counter data persistence
 * Handles all backend communication with error handling and offline support
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface CounterData {
  value: number;
  timestamp: string;
  version: number;
}

export interface SessionData {
  session_id: string;
  start_time: string;
  last_activity: string;
  operations_count: number;
  increments: number;
  decrements: number;
  resets: number;
}

export interface CounterResponse {
  success: boolean;
  data?: CounterData;
  message: string;
}

export interface SessionResponse {
  success: boolean;
  data?: SessionData;
  message: string;
}

export interface BackupData {
  counter: CounterData;
  session: SessionData;
  export_timestamp: string;
  version: number;
}

class ApiService {
  private isOnline: boolean = navigator.onLine;

  constructor() {
    // Monitor online/offline status
    window.addEventListener('online', () => {
      this.isOnline = true;
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  private async makeRequest<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  // Counter operations
  async getCounter(): Promise<CounterResponse> {
    return this.makeRequest<CounterResponse>('/counter');
  }

  async incrementCounter(): Promise<CounterResponse> {
    return this.makeRequest<CounterResponse>('/counter/increment', {
      method: 'POST',
    });
  }

  async decrementCounter(): Promise<CounterResponse> {
    return this.makeRequest<CounterResponse>('/counter/decrement', {
      method: 'POST',
    });
  }

  async resetCounter(): Promise<CounterResponse> {
    return this.makeRequest<CounterResponse>('/counter/reset', {
      method: 'POST',
    });
  }

  // Session operations
  async getSession(): Promise<SessionResponse> {
    return this.makeRequest<SessionResponse>('/session');
  }

  async startSession(): Promise<SessionResponse> {
    return this.makeRequest<SessionResponse>('/session/start', {
      method: 'POST',
    });
  }

  // Backup operations
  async exportBackup(): Promise<{ success: boolean; data: string; filename: string }> {
    return this.makeRequest('/backup/export');
  }

  async importBackup(backupJson: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/backup/import', {
      method: 'POST',
      body: JSON.stringify(backupJson),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.makeRequest('/health');
  }

  // Utility methods
  isOffline(): boolean {
    return !this.isOnline;
  }

  downloadFile(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

export const apiService = new ApiService();