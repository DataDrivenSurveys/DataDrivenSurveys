export interface ResponseData {
  message: {
    id: string;
    text?: string;
  }
}

export interface ResponseError {
  error: string;
}

interface ResponseReturnValue {
  status: number;
  data: ResponseData;
}


export default ResponseReturnValue;
