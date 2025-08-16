import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProductListPage } from './components/ProductListPage';
import { ProductDetailPage } from './components/ProductDetailPage';
import { Counter } from './components/Counter';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="nav-title">Product Catalog</h1>
            <div className="nav-links">
              <a href="/">Products</a>
              <a href="/counter">Counter</a>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ProductListPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/counter" element={<Counter />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;