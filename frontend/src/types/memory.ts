export interface Memory {
  id: string;
  memory: string;
  content?: string;
  score?: number;
  metadata?: {
    tags?: string[];
    category?: string;
    [key: string]: any;
  };
  created_at?: string;
  user_id?: string;
}

export interface MemoryAddRequest {
  content: string;
  user_id: string;
  metadata?: {
    tags?: string[];
    category?: string;
    [key: string]: any;
  };
}

export interface MemorySearchParams {
  query: string;
  user_id: string;
  limit?: number;
}

export interface MemoryListParams {
  user_id: string;
  limit?: number;
}

// Tag-related types
export interface TagSuggestion {
  tags: string[];
  confidence?: number;
}

export interface TagAutocompleteParams {
  prefix: string;
  limit?: number;
}

export interface PopularTagsParams {
  limit?: number;
}
