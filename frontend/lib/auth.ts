const KEY = "liftlens_token";
const EMAIL_KEY = "liftlens_email";

export const getToken = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem(KEY) : null;

export const setToken = (token: string, email: string): void => {
  localStorage.setItem(KEY, token);
  localStorage.setItem(EMAIL_KEY, email);
};

export const clearToken = (): void => {
  localStorage.removeItem(KEY);
  localStorage.removeItem(EMAIL_KEY);
};

export const isAuthenticated = (): boolean => !!getToken();

export const getEmail = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem(EMAIL_KEY) : null;
