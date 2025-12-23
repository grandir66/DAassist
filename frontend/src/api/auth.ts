import apiClient from './client';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  nome: string;
  cognome: string;
  ruolo: string;
}

export interface Tecnico {
  id: number;
  nome: string;
  cognome: string;
  email: string;
  ruolo: string;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    console.log('AuthAPI: Preparing login request for username:', data.username);
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);

    console.log('AuthAPI: Sending POST request to /auth/login');
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      console.log('AuthAPI: Login response status:', response.status);
      console.log('AuthAPI: Login response data:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('AuthAPI: Login request failed');
      console.error('AuthAPI: Error status:', error.response?.status);
      console.error('AuthAPI: Error data:', error.response?.data);
      throw error;
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getTecnici: async (): Promise<Tecnico[]> => {
    const response = await apiClient.get<Tecnico[]>('/auth/tecnici');
    return response.data;
  },
};
