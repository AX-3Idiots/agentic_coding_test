import React from "react";
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  Rating,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

interface FilterSidebarProps {
  onFilterChange: (filters: any) => void;
}

const FilterSidebar: React.FC<FilterSidebarProps> = ({ onFilterChange }) => {
  const [priceRange, setPriceRange] = React.useState<number[]>([0, 1000]);
  const [selectedCategories, setSelectedCategories] = React.useState<string[]>([]);
  const [selectedBrands, setSelectedBrands] = React.useState<string[]>([]);
  const [minRating, setMinRating] = React.useState<number>(0);

  const categories = ["Electronics", "Fashion", "Home", "Sports", "Books"];
  const brands = ["Apple", "Samsung", "Nike", "Adidas", "Sony"];

  const handlePriceChange = (event: Event, newValue: number | number[]) => {
    setPriceRange(newValue as number[]);
    onFilterChange({ priceRange: newValue, selectedCategories, selectedBrands, minRating });
  };

  const handleCategoryChange = (category: string) => {
    const newCategories = selectedCategories.includes(category)
      ? selectedCategories.filter(c => c !== category)
      : [...selectedCategories, category];
    setSelectedCategories(newCategories);
    onFilterChange({ priceRange, selectedCategories: newCategories, selectedBrands, minRating });
  };

  const handleBrandChange = (brand: string) => {
    const newBrands = selectedBrands.includes(brand)
      ? selectedBrands.filter(b => b !== brand)
      : [...selectedBrands, brand];
    setSelectedBrands(newBrands);
    onFilterChange({ priceRange, selectedCategories, selectedBrands: newBrands, minRating });
  };

  const handleRatingChange = (event: React.SyntheticEvent, newValue: number | null) => {
    const rating = newValue || 0;
    setMinRating(rating);
    onFilterChange({ priceRange, selectedCategories, selectedBrands, minRating: rating });
  };

  return (
    <Box sx={{ width: 280, p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Price Range</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ px: 2 }}>
            <Slider
              value={priceRange}
              onChange={handlePriceChange}
              valueLabelDisplay="auto"
              min={0}
              max={1000}
              step={10}
            />
            <Typography variant="body2" color="text.secondary">
              ${priceRange[0]} - ${priceRange[1]}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Categories</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {categories.map((category) => (
              <FormControlLabel
                key={category}
                control={
                  <Checkbox
                    checked={selectedCategories.includes(category)}
                    onChange={() => handleCategoryChange(category)}
                  />
                }
                label={category}
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Brands</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {brands.map((brand) => (
              <FormControlLabel
                key={brand}
                control={
                  <Checkbox
                    checked={selectedBrands.includes(brand)}
                    onChange={() => handleBrandChange(brand)}
                  />
                }
                label={brand}
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Rating</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Rating
              value={minRating}
              onChange={handleRatingChange}
            />
            <Typography variant="body2">& up</Typography>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default FilterSidebar;
