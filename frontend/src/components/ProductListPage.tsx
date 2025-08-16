import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProductApi } from '../services/productApi';
import { Product, ProductFilters } from '../types/product';
import { debounce } from '../utils/debounce';

export const ProductListPage: React.FC = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  
  // Filter state
  const [filters, setFilters] = useState<ProductFilters>({
    q: '',
    category: '',
    brand: '',
    in_stock: undefined,
    min_price: undefined,
    max_price: undefined,
    page: 1,
    per_page: 12
  });
  
  // Pagination state
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    per_page: 12,
    total_pages: 0
  });

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((searchFilters: ProductFilters) => {
      loadProducts(searchFilters);
    }, 300),
    []
  );

  const loadProducts = async (searchFilters: ProductFilters = filters) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ProductApi.getProducts(searchFilters);
      setProducts(response.products);
      setPagination({
        total: response.total,
        page: response.page,
        per_page: response.per_page,
        total_pages: response.total_pages
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const loadFilterOptions = async () => {
    try {
      const [categoriesData, brandsData] = await Promise.all([
        ProductApi.getCategories(),
        ProductApi.getBrands()
      ]);
      setCategories(categoriesData);
      setBrands(brandsData);
    } catch (err) {
      console.error('Failed to load filter options:', err);
    }
  };

  useEffect(() => {
    loadProducts();
    loadFilterOptions();
  }, []);

  const handleFilterChange = (key: keyof ProductFilters, value: any) => {
    const newFilters = {
      ...filters,
      [key]: value,
      page: key === 'page' ? value : 1 // Reset to page 1 for non-page filters
    };
    
    setFilters(newFilters);
    
    if (key === 'q') {
      // Use debounced search for text input
      debouncedSearch(newFilters);
    } else {
      // Immediate search for other filters
      loadProducts(newFilters);
    }
  };

  const handleProductClick = (productId: number) => {
    navigate(`/products/${productId}`);
  };

  const handlePageChange = (newPage: number) => {
    handleFilterChange('page', newPage);
  };

  const renderPagination = () => {
    if (pagination.total_pages <= 1) return null;

    const pages = [];
    const currentPage = pagination.page;
    const totalPages = pagination.total_pages;
    
    // Show first page
    if (currentPage > 3) {
      pages.push(1);
      if (currentPage > 4) {
        pages.push('...');
      }
    }
    
    // Show pages around current page
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
      pages.push(i);
    }
    
    // Show last page
    if (currentPage < totalPages - 2) {
      if (currentPage < totalPages - 3) {
        pages.push('...');
      }
      pages.push(totalPages);
    }

    return (
      <div className="pagination">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        
        {pages.map((page, index) => (
          <button
            key={index}
            onClick={() => typeof page === 'number' && handlePageChange(page)}
            className={page === currentPage ? 'active' : ''}
            disabled={typeof page !== 'number'}
          >
            {page}
          </button>
        ))}
        
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
        
        <div className="pagination-info">
          Showing {((currentPage - 1) * pagination.per_page) + 1} to {Math.min(currentPage * pagination.per_page, pagination.total)} of {pagination.total} products
        </div>
      </div>
    );
  };

  return (
    <div className="product-list-container">
      <h1>Product Catalog</h1>
      
      {/* Search and Filters */}
      <div className="search-and-filters">
        <input
          type="text"
          className="search-bar"
          placeholder="Search products..."
          value={filters.q || ''}
          onChange={(e) => handleFilterChange('q', e.target.value)}
        />
        
        <div className="filters">
          <div className="filter-group">
            <label>Category</label>
            <select
              value={filters.category || ''}
              onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>Brand</label>
            <select
              value={filters.brand || ''}
              onChange={(e) => handleFilterChange('brand', e.target.value || undefined)}
            >
              <option value="">All Brands</option>
              {brands.map(brand => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>Availability</label>
            <select
              value={filters.in_stock === undefined ? '' : filters.in_stock.toString()}
              onChange={(e) => {
                const value = e.target.value;
                handleFilterChange('in_stock', value === '' ? undefined : value === 'true');
              }}
            >
              <option value="">All Products</option>
              <option value="true">In Stock</option>
              <option value="false">Out of Stock</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Min Price</label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              value={filters.min_price || ''}
              onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
            />
          </div>
          
          <div className="filter-group">
            <label>Max Price</label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="999.99"
              value={filters.max_price || ''}
              onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && <div className="loading">Loading products...</div>}

      {/* Error State */}
      {error && <div className="error">Error: {error}</div>}

      {/* Products Grid */}
      {!loading && !error && (
        <>
          <div className="products-grid">
            {products.map(product => (
              <div
                key={product.id}
                className="product-card"
                onClick={() => handleProductClick(product.id)}
              >
                {product.image_url && (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="product-image"
                  />
                )}
                <div className="product-info">
                  <h3 className="product-name">{product.name}</h3>
                  <div className="product-price">${product.price.toFixed(2)}</div>
                  <p className="product-description">{product.description}</p>
                  <div className="product-meta">
                    <span>{product.category} • {product.brand}</span>
                    <span className={`stock-status ${product.in_stock ? 'in-stock' : 'out-of-stock'}`}>
                      {product.in_stock ? `${product.stock_quantity} in stock` : 'Out of stock'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {products.length === 0 && !loading && (
            <div className="loading">No products found matching your criteria.</div>
          )}

          {renderPagination()}
        </>
      )}
    </div>
  );
};