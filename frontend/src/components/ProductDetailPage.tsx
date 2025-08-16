import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProductApi } from '../services/productApi';
import { Product } from '../types/product';

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProduct = async () => {
      if (!id) {
        setError('Product ID is required');
        setLoading(false);
        return;
      }

      const productId = parseInt(id, 10);
      if (isNaN(productId)) {
        setError('Invalid product ID');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await ProductApi.getProduct(productId);
        setProduct(response.product || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load product');
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [id]);

  const handleBackClick = () => {
    navigate('/');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return <div className="loading">Loading product details...</div>;
  }

  if (error) {
    return (
      <div className="product-detail-container">
        <button onClick={handleBackClick} className="back-link">
          ← Back to Products
        </button>
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-detail-container">
        <button onClick={handleBackClick} className="back-link">
          ← Back to Products
        </button>
        <div className="error">Product not found</div>
      </div>
    );
  }

  return (
    <div className="product-detail-container">
      <button onClick={handleBackClick} className="back-link">
        ← Back to Products
      </button>
      
      <div className="product-detail">
        <div className="product-detail-image-container">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="product-detail-image"
            />
          ) : (
            <div className="product-detail-image product-placeholder">
              No Image Available
            </div>
          )}
        </div>
        
        <div className="product-detail-info">
          <h1>{product.name}</h1>
          
          <div className="product-detail-price">
            ${product.price.toFixed(2)}
          </div>
          
          <p className="product-detail-description">
            {product.description}
          </p>
          
          <div className="product-detail-meta">
            <div className="product-detail-meta-item">
              <strong>Category</strong>
              <span>{product.category}</span>
            </div>
            
            <div className="product-detail-meta-item">
              <strong>Brand</strong>
              <span>{product.brand}</span>
            </div>
            
            <div className="product-detail-meta-item">
              <strong>Availability</strong>
              <span className={`stock-status ${product.in_stock ? 'in-stock' : 'out-of-stock'}`}>
                {product.in_stock 
                  ? `${product.stock_quantity} units in stock`
                  : 'Out of stock'
                }
              </span>
            </div>
            
            <div className="product-detail-meta-item">
              <strong>Product ID</strong>
              <span>#{product.id}</span>
            </div>
            
            <div className="product-detail-meta-item">
              <strong>Added</strong>
              <span>{formatDate(product.created_at)}</span>
            </div>
            
            <div className="product-detail-meta-item">
              <strong>Last Updated</strong>
              <span>{formatDate(product.updated_at)}</span>
            </div>
          </div>
          
          <div className="product-actions">
            {product.in_stock ? (
              <button className="btn btn-primary" disabled>
                Add to Cart (Demo)
              </button>
            ) : (
              <button className="btn btn-secondary" disabled>
                Out of Stock
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};