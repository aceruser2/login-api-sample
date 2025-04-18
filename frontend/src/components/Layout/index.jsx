import React from "react";
import { Box } from "@mui/material";

const Layout = ({ children }) => (
  <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
    {/* You can add a header or nav here if needed */}
    {children}
  </Box>
);

export { Layout };
