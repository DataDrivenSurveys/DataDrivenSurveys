import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const axiosInstanceWithToken = axios.create({
  baseURL: API_URL,
});

const axiosInstanceWithoutToken = axios.create({
  baseURL: API_URL,
});

axiosInstanceWithToken.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('tokenDDS');
        if (!token) {
            throw new axios.Cancel('Token missing');
        }
        config.headers['Authorization'] = 'Bearer ' + token;
        return config;
    }
);


const handleResponse = (response) => {
    const customResponse = {
      data: response.data,
      on: (statusCodeRange, callback) => {
        // statusCodeRange: 1xx, 2xx etc.
        const status = response.status;

        const hundreds = parseInt(statusCodeRange[0]);
        const rangeStart = hundreds * 100;
        const rangeEnd = rangeStart + 99;

        if (status >= rangeStart && status <= rangeEnd) {
          callback(status, response.data);
        }
        return customResponse;
      },
      status: response.status,
    };
    return customResponse;
  };

  const handleError = (error) => {
    if (error.response) {
      const customError = {
        error: error.response,
        on: (statusCodeRange, callback) => {
          const status = error.response.status;

          const hundreds = parseInt(statusCodeRange[0]);
          const rangeStart = hundreds * 100;
          const rangeEnd = rangeStart + 99;

          if (status >= rangeStart && status <= rangeEnd) {
            callback(status, error.response.data);
          }
          return customError;
        },
        status: error.response.status,
      };
      return customError;
    } else if (error.request) {
      console.log('error.request', error.request);
      return {
        on: () => {},
      }
    } else {
      console.log('error.message', error.message);
      return {
        on: () => {},
      }
    }
  };

/*

Each http functions returns an object with the following methods:
{
  data: json ,
  on: a callback function that is called based on the http status range
  status: http status code
}

*/


export const GET = async (endpoint, use_token = true) => {
  try {
    const response = use_token ? await axiosInstanceWithToken.get(endpoint) : await axiosInstanceWithoutToken.get(endpoint);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

export const POST = async (endpoint, data, use_token = true) => {
  try {
      const response = use_token ? await axiosInstanceWithToken.post(endpoint, data) : await axiosInstanceWithoutToken.post(endpoint, data);
      return handleResponse(response);
  } catch (error) {
      return handleError(error);
  }
};

export const PUT = async (endpoint, data, use_token = true) => {
  try {
    const response = use_token ? await axiosInstanceWithToken.put(endpoint, data) : await axiosInstanceWithoutToken.put(endpoint, data);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

export const DEL = async (endpoint, use_token = true) => {
  try {
    const response = use_token ? await axiosInstanceWithToken.delete(endpoint) : await axiosInstanceWithoutToken.delete(endpoint);
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

export const POST_BLOB = async (endpoint, data, use_token = true) => {
  try {
    const response = use_token ? await axiosInstanceWithToken.post(endpoint, data, { responseType: 'blob' }) : await axiosInstanceWithoutToken.post(endpoint, data, { responseType: 'blob' });
    return handleResponse(response);
  } catch (error) {
    return handleError(error);
  }
};

export const PUBLIC_GET = async (endpoint)         => GET(endpoint, false);
export const PUBLIC_POST = async (endpoint, data)  => POST(endpoint, data, false);
export const PUBLIC_POST_BLOB = async (endpoint, data)  => POST_BLOB(endpoint, data, false);
export const PUBLIC_PUT = async (endpoint, data)   => PUT(endpoint, data, false);
export const PUBLIC_DEL = async (endpoint)         => DEL(endpoint, false);
