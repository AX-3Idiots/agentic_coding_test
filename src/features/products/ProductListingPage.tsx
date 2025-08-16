import React from "react";
import {
  Container,
  Grid,
  Box,
  Typography,
  Pagination,
  Drawer,
  IconButton,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import Header from "../../components/common/Header";
import ProductCard, { Product } from "../../components/ui/ProductCard";
import FilterSidebar from "../../components/ui/FilterSidebar";

// Mock data for demonstration
const mockProducts: Product[] = [
  {
    id: 1,
    title: "Wireless Bluetooth Headphones",
    price: 99.99,
    image: "/images/product-placeholder.png",
    rating: 4.5,
    category: "Electronics",
    brand: "Sony",
  },
  {
    id: 2,
    title: "Smart Fitness Watch",
    price: 199.99,
    image: "/images/product-placeholder.png",
    rating: 4.2,
    category: "Electronics",
    brand: "Apple",
  },
  {
    id: 3,
    title: "Running Shoes",
    price: 129.99,
    image: "/images/product-placeholder.png",
    rating: 4.7,
    category: "Sports",
    brand: "Nike",
  },
  {
    id: 4,
    title: "Cotton T-Shirt",
    price: 29.99,
    image: "/images/product-placeholder.png",
    rating: 4.0,
    category: "Fashion",
    brand: "Adidas",
  },
  {
    id: 5,
    title: "Smartphone Case",
    price: 19.99,
    image: "/images/product-placeholder.png",
    rating: 4.3,
    category: "Electronics",
    brand: "Samsung",
  },
  {
    id: 6,
    title: "Coffee Maker",
    price: 89.99,
    image: "/images/product-placeholder.png",
    rating: 4.6,
    category: "Home",
    brand: "Sony",
  },
];

const ProductListingPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [products, setProducts] = React.useState<Product[]>(mockProducts);
  const [filteredProducts, setFilteredProducts] = React.useState<Product[]>(mockProducts);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [currentPage, setCurrentPage] = React.useState(1);
  const [mobileFilterOpen, setMobileFilterOpen] = React.useState(false);
  const productsPerPage = 8;

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    filterProducts(query, {});
  };

  const handleFilterChange = (filters: any) => {
    filterProducts(searchQuery, filters);
  };

  const filterProducts = (query: string, filters: any) => {
    let filtered = products;

    // Search filter
    if (query) {
      filtered = filtered.filter(product =>
        product.title.toLowerCase().includes(query.toLowerCase()) ||
        product.category.toLowerCase().includes(query.toLowerCase()) ||
        product.brand.toLowerCase().includes(query.toLowerCase())
      );
    }

    // Price filter
    if (filters.priceRange) {
      filtered = filtered.filter(product =>
        product.price >= filters.priceRange[0] && product.price <= filters.priceRange[1]
      );
    }

    // Category filter
    if (filters.selectedCategories && filters.selectedCategories.length > 0) {
      filtered = filtered.filter(product =>
        filters.selectedCategories.includes(product.category)
      );
    }

    // Brand filter
    if (filters.selectedBrands && filters.selectedBrands.length > 0) {
      filtered = filtered.filter(product =>
        filters.selectedBrands.includes(product.brand)
      );
    }

    // Rating filter
    if (filters.minRating) {
      filtered = filtered.filter(product => product.rating >= filters.minRating);
    }

    setFilteredProducts(filtered);
    setCurrentPage(1);
  };

  const handleAddToCart = (product: Product) => {
    console.log("Added to cart:", product);
    // TODO: Implement cart functionality
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setCurrentPage(value);
  };

  const startIndex = (currentPage - 1) * productsPerPage;
  const endIndex = startIndex + productsPerPage;
  const currentProducts = filteredProducts.slice(startIndex, endIndex);
  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header onSearch={handleSearch} />
      
      <Container maxWidth="xl" sx={{ flex: 1, py: 3 }}>
        <Box sx={{ display: "flex", gap: 3 }}>
          {/* Desktop Filter Sidebar */}
          {!isMobile && (
            <Box sx={{ flexShrink: 0 }}>
              <FilterSidebar onFilterChange={handleFilterChange} />
            </Box>
          )}

          {/* Mobile Filter Button */}
          {isMobile && (
            <Box sx={{ position: "fixed", top: 80, right: 16, zIndex: 1000 }}>
              <IconButton
                onClick={() => setMobileFilterOpen(true)}
                sx={{ bgcolor: "primary.main", color: "white" }}
              >
                <FilterListIcon />
              </IconButton>
            </Box>
          )}

          {/* Mobile Filter Drawer */}
          <Drawer
            anchor="left"
            open={mobileFilterOpen}
            onClose={() => setMobileFilterOpen(false)}
          >
            <FilterSidebar onFilterChange={handleFilterChange} />
          </Drawer>

          {/* Main Content */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" gutterBottom>
              Products ({filteredProducts.length})
            </Typography>

            <Grid container spacing={3}>
              {currentProducts.map((product) => (
                <Grid
                  item
                  xs={12}
                  sm={6}
                  md={isMobile ? 6 : 4}
                  lg={isMobile ? 4 : 3}
                  key={product.id}
                >
                  <ProductCard
                    product={product}
                    onAddToCart={handleAddToCart}
                  />
                </Grid>
              ))}
            </Grid>

            {filteredProducts.length === 0 && (
              <Box sx={{ textAlign: "center", py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                  No products found matching your criteria.
                </Typography>
              </Box>
            )}

            {totalPages > 1 && (
              <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                <Pagination
                  count={totalPages}
                  page={currentPage}
                  onChange={handlePageChange}
                  color="primary"
                  size="large"
                />
              </Box>
            )}
          </Box>
        </Box>
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          bgcolor: "grey.100",
          py: 4,
          mt: 4,
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            © 2024 ShopMall. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default ProductListingPage;
