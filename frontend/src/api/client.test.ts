import { describe, it, expect } from 'vitest';
import { apiClient } from './client';

describe('apiClient', () => {
  it('should have a getBaseUrl method that returns a string', () => {
    expect(apiClient.getBaseUrl).toBeDefined();
    expect(typeof apiClient.getBaseUrl()).toBe('string');
  });

  it('should have get method', () => {
    expect(apiClient.get).toBeDefined();
    expect(typeof apiClient.get).toBe('function');
  });

  it('should have post method', () => {
    expect(apiClient.post).toBeDefined();
    expect(typeof apiClient.post).toBe('function');
  });

  it('should have put method', () => {
    expect(apiClient.put).toBeDefined();
    expect(typeof apiClient.put).toBe('function');
  });

  it('should have delete method', () => {
    expect(apiClient.delete).toBeDefined();
    expect(typeof apiClient.delete).toBe('function');
  });

  it('should return base URL containing api/v1', () => {
    const baseUrl = apiClient.getBaseUrl();
    expect(baseUrl).toContain('api/v1');
  });
});
