import { Product, ProductListResponse, ProductResponse, ProductFilters } from '../types/product';

const API_BASE_URL = 'http://localhost:8000/api';

export class ProductApi {
  static async getProducts(filters: ProductFilters = {}): Promise<ProductListResponse> {
    const params = new URLSearchParams();
    
    // Add non-empty filters to params
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    const url = `${API_BASE_URL}/products${params.toString() ? `?${params.toString()}` : ''}`;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ProductListResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  }

  static async getProduct(id: number): Promise<ProductResponse> {
    const url = `${API_BASE_URL}/products/${id}`;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Product not found');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ProductResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }

  static async getCategories(): Promise<string[]> {
    try {
      const response = await this.getProducts({ per_page: 100 }); // Get all products to extract categories
      const categories = [...new Set(response.products.map(p => p.category))];
      return categories.sort();
    } catch (error) {
      console.error('Error fetching categories:', error);
      return [];
    }
  }

  static async getBrands(): Promise<string[]> {
    try {
      const response = await this.getProducts({ per_page: 100 }); // Get all products to extract brands
      const brands = [...new Set(response.products.map(p => p.brand))];
      return brands.sort();
    } catch (error) {
      console.error('Error fetching brands:', error);
      return [];
    }
  }
}