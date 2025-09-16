export interface User {
  id: string;
  username: string;
  email?: string;
  full_name?: string;
  disabled?: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

