/**
 * API utility functions for calling Kosty backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ApiRequestConfig {
  user_role_arn?: string;
  external_id?: string;
  regions?: string[];
  [key: string]: any;
}

/**
 * Make a GET request to the API
 */
export async function apiGet(endpoint: string) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API request failed');
  }
  return response.json();
}

/**
 * Make a POST request to the API
 */
export async function apiPost(endpoint: string, data?: ApiRequestConfig) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data || {}),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API request failed');
  }
  
  return response.json();
}
