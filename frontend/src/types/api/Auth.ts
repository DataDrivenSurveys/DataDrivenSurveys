export interface ResponseSignIn {
  token: string;
}

export interface User {
  email: string;
  firstname: string;
  lastname: string;
}

export interface ResponseSession {
  logged_in_as: User;
}
