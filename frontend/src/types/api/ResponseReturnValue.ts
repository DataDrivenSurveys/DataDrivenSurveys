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
  data: ResponseData;
  status: number;
}

export default ResponseReturnValue;
