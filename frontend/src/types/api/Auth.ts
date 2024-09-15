export interface ResponseSignIn {
  token: string;
}

export interface User {
  firstname: string;
  lastname: string;
  email: string;
}

export interface ResponseSession {
  logged_in_as: User;
}
