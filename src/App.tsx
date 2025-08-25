import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { AppBar, Toolbar, Typography, Container, Card, CardContent } from "@mui/material";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div">
            Digital Timer
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              Welcome to Digital Timer
            </Typography>
            <Typography variant="body1" align="center">
              A modern timer application with countdown and stopwatch functionality.
            </Typography>
          </CardContent>
        </Card>
      </Container>
    </ThemeProvider>
  );
}

export default App;
