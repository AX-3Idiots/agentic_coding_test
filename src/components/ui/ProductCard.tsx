import React from "react";
import {
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  Rating,
  Box,
} from "@mui/material";
import { AddShoppingCart as AddShoppingCartIcon } from "@mui/icons-material";

export interface Product {
  id: number;
  title: string;
  price: number;
  image: string;
  rating: number;
  category: string;
  brand: string;
}

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToCart }) => {
  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardMedia
        component="img"
        height="200"
        image={product.image}
        alt={product.title}
        sx={{ objectFit: "cover" }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div" noWrap>
          {product.title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
          <Rating value={product.rating} readOnly size="small" />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            ({product.rating})
          </Typography>
        </Box>
        <Typography variant="h6" color="primary" fontWeight="bold">
          ${product.price.toFixed(2)}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          startIcon={<AddShoppingCartIcon />}
          fullWidth
          onClick={() => onAddToCart(product)}
        >
          Add to Cart
        </Button>
      </CardActions>
    </Card>
  );
};

export default ProductCard;
