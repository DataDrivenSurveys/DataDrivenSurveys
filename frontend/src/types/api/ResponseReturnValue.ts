export interface MessageData {
  id: string;
  text?: string;
}

export interface ResponseData {
  message: MessageData;
}

export interface ResponseError {
  error: string;
}

interface ResponseReturnValue {
  status: number;
  data: ResponseData;
}


export default ResponseReturnValue;
