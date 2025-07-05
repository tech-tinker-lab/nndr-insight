import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; // If you have global styles or Tailwind

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);