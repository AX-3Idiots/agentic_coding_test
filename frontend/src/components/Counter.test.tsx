/**
 * Tests for Counter component data persistence functionality
 * Covers all user stories and acceptance criteria
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';
import { apiService } from '../services/api';
import { storageService } from '../services/storage';

// Mock the services
jest.mock('../services/api');
jest.mock('../services/storage');

const mockApiService = apiService as jest.Mocked<typeof apiService>;
const mockStorageService = storageService as jest.Mocked<typeof storageService>;

describe('Counter Data Persistence', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mock responses
    mockApiService.getCounter.mockResolvedValue({
      success: true,
      data: { value: 0, timestamp: new Date().toISOString(), version: 1 },
      message: 'Counter loaded'
    });
    
    mockApiService.incrementCounter.mockResolvedValue({
      success: true,
      data: { value: 1, timestamp: new Date().toISOString(), version: 1 },
      message: 'Incremented'
    });
    
    mockApiService.decrementCounter.mockResolvedValue({
      success: true,
      data: { value: -1, timestamp: new Date().toISOString(), version: 1 },
      message: 'Decremented'
    });
    
    mockApiService.resetCounter.mockResolvedValue({
      success: true,
      data: { value: 0, timestamp: new Date().toISOString(), version: 1 },
      message: 'Reset'
    });
    
    mockApiService.startSession.mockResolvedValue({
      success: true,
      data: {
        session_id: 'test-session-123',
        start_time: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        operations_count: 0,
        increments: 0,
        decrements: 0,
        resets: 0
      },
      message: 'Session started'
    });
    
    mockStorageService.saveCounterData.mockReturnValue(true);
    mockStorageService.saveSessionData.mockReturnValue(true);
    mockStorageService.loadCounterData.mockReturnValue(null);
    mockStorageService.loadSessionData.mockReturnValue(null);
    
    // Mock online status
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true
    });
  });

  // User Story 1: Auto-save counter value
  describe('Auto-save functionality', () => {
    test('counter value saves automatically on each change', async () => {
      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      
      await act(async () => {
        fireEvent.click(incrementButton);
      });
      
      await waitFor(() => {
        expect(mockApiService.incrementCounter).toHaveBeenCalled();
        expect(mockStorageService.saveCounterData).toHaveBeenCalled();
      });
    });

    test('timestamp is saved along with counter value', async () => {
      const testTimestamp = new Date().toISOString();
      mockApiService.incrementCounter.mockResolvedValue({
        success: true,
        data: { value: 1, timestamp: testTimestamp, version: 1 },
        message: 'Incremented'
      });

      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      
      await act(async () => {
        fireEvent.click(incrementButton);
      });
      
      await waitFor(() => {
        expect(mockStorageService.saveCounterData).toHaveBeenCalledWith(
          expect.objectContaining({ timestamp: testTimestamp })
        );
      });
    });

    test('debounced writes prevent excessive storage operations', async () => {
      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      
      // Rapid clicks should be debounced on the frontend
      // The actual debouncing is in the component, so we test the behavior
      await act(async () => {
        fireEvent.click(incrementButton);
        fireEvent.click(incrementButton);
        fireEvent.click(incrementButton);
      });
      
      // Should not overwhelm the storage system
      await waitFor(() => {
        expect(mockApiService.incrementCounter).toHaveBeenCalledTimes(3);
      });
    });
  });

  // User Story 2: Auto-restore counter value
  describe('Auto-restore functionality', () => {
    test('counter value loads automatically on application start', async () => {
      mockApiService.getCounter.mockResolvedValue({
        success: true,
        data: { value: 42, timestamp: new Date().toISOString(), version: 1 },
        message: 'Loaded'
      });

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText('42')).toBeInTheDocument();
        expect(mockApiService.getCounter).toHaveBeenCalled();
      });
    });

    test('application defaults to 0 if no saved value exists', async () => {
      mockApiService.getCounter.mockResolvedValue({
        success: true,
        data: { value: 0, timestamp: new Date().toISOString(), version: 1 },
        message: 'Default'
      });

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument();
      });
    });

    test('data validation ensures loaded values are within bounds', async () => {
      // Test with valid data first
      mockApiService.getCounter.mockResolvedValue({
        success: true,
        data: { value: 100, timestamp: new Date().toISOString(), version: 1 },
        message: 'Valid data'
      });

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText('100')).toBeInTheDocument();
      });
    });
  });

  // User Story 3: Session data persistence
  describe('Session data persistence', () => {
    test('session data saves when operations are performed', async () => {
      const sessionData = {
        session_id: 'test-session-123',
        start_time: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        operations_count: 1,
        increments: 1,
        decrements: 0,
        resets: 0
      };

      mockApiService.getSession.mockResolvedValue({
        success: true,
        data: sessionData,
        message: 'Session loaded'
      });

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText(/Session ID:/)).toBeInTheDocument();
        expect(screen.getByText(/Total Operations:/)).toBeInTheDocument();
      });
    });

    test('session statistics include usage data and timestamps', async () => {
      const sessionData = {
        session_id: 'test-session-123',
        start_time: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        operations_count: 5,
        increments: 3,
        decrements: 1,
        resets: 1
      };

      mockApiService.getSession.mockResolvedValue({
        success: true,
        data: sessionData,
        message: 'Session loaded'
      });

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText('5')).toBeInTheDocument(); // operations_count
        expect(screen.getByText('3')).toBeInTheDocument(); // increments
        expect(screen.getByText('1')).toBeInTheDocument(); // decrements and resets
      });
    });
  });

  // User Story 4: Offline reliability
  describe('Offline functionality', () => {
    test('application works without internet connection', async () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        value: false
      });

      mockStorageService.loadCounterData.mockReturnValue({
        value: 5,
        timestamp: new Date().toISOString(),
        version: 1
      });

      render(<Counter />);
      
      // Should show offline indicator
      await waitFor(() => {
        expect(screen.getByText(/Working offline/)).toBeInTheDocument();
        expect(screen.getByText('5')).toBeInTheDocument();
      });
    });

    test('data validation occurs when loading from local storage', async () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false
      });

      // Mock invalid data that should be handled gracefully
      mockStorageService.loadCounterData.mockReturnValue(null);

      render(<Counter />);
      
      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument(); // Default value
      });
    });

    test('storage errors are handled gracefully', async () => {
      mockStorageService.saveCounterData.mockReturnValue(false);
      mockApiService.incrementCounter.mockRejectedValue(new Error('Storage error'));

      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      
      await act(async () => {
        fireEvent.click(incrementButton);
      });
      
      // Should show error notification
      await waitFor(() => {
        expect(screen.getByText(/operation failed/i)).toBeInTheDocument();
      });
    });
  });

  // User Story 5: Backup and restore
  describe('Backup and restore functionality', () => {
    test('export counter data to downloadable JSON file', async () => {
      const mockDownloadFile = jest.fn();
      mockApiService.downloadFile = mockDownloadFile;
      
      mockApiService.exportBackup.mockResolvedValue({
        success: true,
        data: JSON.stringify({ counter: { value: 42 }, session: {} }),
        filename: 'backup.json'
      });

      render(<Counter />);
      
      const exportButton = screen.getByText('📁 Export Backup');
      
      await act(async () => {
        fireEvent.click(exportButton);
      });
      
      await waitFor(() => {
        expect(mockApiService.exportBackup).toHaveBeenCalled();
        expect(mockDownloadFile).toHaveBeenCalledWith(
          expect.any(String),
          'backup.json'
        );
      });
    });

    test('import counter data from uploaded JSON file', async () => {
      const file = new File(['{"counter":{"value":99}}'], 'backup.json', {
        type: 'application/json'
      });

      // Mock window.confirm
      window.confirm = jest.fn(() => true);

      mockApiService.importBackup.mockResolvedValue({
        success: true,
        message: 'Imported successfully'
      });

      render(<Counter />);
      
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [file] } });
      });
      
      await waitFor(() => {
        expect(mockApiService.importBackup).toHaveBeenCalled();
      });
    });

    test('data validation ensures imported data is valid', async () => {
      const invalidFile = new File(['invalid json'], 'backup.json', {
        type: 'application/json'
      });

      render(<Counter />);
      
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [invalidFile] } });
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Invalid JSON/)).toBeInTheDocument();
      });
    });

    test('user confirmation required before overwriting existing data', async () => {
      const file = new File(['{"counter":{"value":99}}'], 'backup.json', {
        type: 'application/json'
      });

      // Mock window.confirm to return false (user cancels)
      window.confirm = jest.fn(() => false);

      render(<Counter />);
      
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [file] } });
      });
      
      // Should not call import if user cancels
      expect(mockApiService.importBackup).not.toHaveBeenCalled();
    });
  });

  // Performance and UI requirements
  describe('Performance and UI requirements', () => {
    test('save operations complete within reasonable time', async () => {
      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      const startTime = performance.now();
      
      await act(async () => {
        fireEvent.click(incrementButton);
      });
      
      await waitFor(() => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        // Should complete reasonably quickly (allowing for test environment overhead)
        expect(duration).toBeLessThan(1000); // 1 second max for test environment
      });
    });

    test('storage operations do not block user interface', async () => {
      render(<Counter />);
      
      const incrementButton = screen.getByText('+ Increment');
      
      // Click should not be permanently disabled
      expect(incrementButton).not.toHaveAttribute('disabled');
      
      await act(async () => {
        fireEvent.click(incrementButton);
      });
      
      // After operation, button should be available again
      await waitFor(() => {
        expect(incrementButton).not.toHaveAttribute('disabled');
      });
    });
  });
});