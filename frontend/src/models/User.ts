// User model for both frontend and backend usage

export interface User {
  id: string | number;
  username: string;
  email?: string;
  roles?: string[];
  isActive?: boolean;
  // Add more fields as needed based on your backend user object
}

export interface AuthToken {
  access_token: string;
  token_type?: string;
  expires_in?: number;
}
