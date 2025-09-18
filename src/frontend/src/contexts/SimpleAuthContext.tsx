import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react';
import { authService } from '../services/api';
import { User, LoginCredentials } from '../types/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Cargar token al inicializar
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          setToken(storedToken);
          setUser({
            id: '1',
            username: 'user',
            email: '',
            full_name: 'Usuario',
            disabled: false
          });
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      console.log('Intentando login con:', credentials);
      const response = await authService.login(credentials);
      console.log('Respuesta del servidor:', response);
      
      const { access_token } = response;
      
      if (!access_token) {
        throw new Error('No se recibió token de acceso');
      }
      
      setToken(access_token);
      localStorage.setItem('token', access_token);
      
      setUser({
        id: '1',
        username: credentials.username,
        email: '',
        full_name: credentials.username,
        disabled: false
      });
      
      console.log('Login exitoso');
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  }, []);

  const value = useMemo(() => ({
    user,
    token,
    login,
    logout,
    loading
  }), [user, token, login, logout, loading]); // ✅ Todas las dependencias incluidas

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
