export interface OllamaModel {
  name: string;
  size?: string;
  modified_at?: string;
  details?: {
    format?: string;
    family?: string;
    parameter_size?: string;
    quantization_level?: string;
    [key: string]: any;
  };
}

export interface OllamaStatus {
  status: 'online' | 'offline';
  version?: string;
}
