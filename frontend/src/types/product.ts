export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  brand: string;
  in_stock: boolean;
  stock_quantity: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  success: boolean;
  products: Product[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  message: string;
}

export interface ProductResponse {
  success: boolean;
  product?: Product;
  message: string;
}

export interface ProductFilters {
  q?: string;
  category?: string;
  brand?: string;
  in_stock?: boolean;
  min_price?: number;
  max_price?: number;
  page?: number;
  per_page?: number;
}