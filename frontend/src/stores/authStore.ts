import { create } from 'zustand';
import { authApi, type User } from '@/api/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (username: string, password: string) => {
    console.log('AuthStore: Starting login for username:', username);
    try {
      const response = await authApi.login({ username, password });
      console.log('AuthStore: Login API response received:', {
        hasAccessToken: !!response.access_token,
        hasRefreshToken: !!response.refresh_token
      });

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      console.log('AuthStore: Tokens saved to localStorage');

      console.log('AuthStore: Fetching current user info...');
      const user = await authApi.getCurrentUser();
      console.log('AuthStore: User info received:', user);

      set({ user, isAuthenticated: true });
      console.log('AuthStore: Login successful, state updated');
    } catch (error) {
      console.error('AuthStore: Login failed:', error);
      throw error;
    }
  },

  logout: () => {
    authApi.logout();
    set({ user: null, isAuthenticated: false });
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
