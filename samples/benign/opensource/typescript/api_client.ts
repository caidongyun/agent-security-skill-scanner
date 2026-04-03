// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520318

#!/usr/bin/env ts-node
/**
 * API 客户端 - 良性
 */
import axios, { AxiosInstance } from 'axios';

class ApiClient {
  private client: AxiosInstance;
  
  constructor(baseUrl: string, apiKey: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });
  }
  
  async getData(endpoint: string): Promise<any> {
    const response = await this.client.get(endpoint);
    return response.data;
  }
  
  async postData(endpoint: string, data: any): Promise<any> {
    const response = await this.client.post(endpoint, data);
    return response.data;
  }
}

const client = new ApiClient('https://api.example.com', 'your-api-key');
