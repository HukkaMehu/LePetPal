import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { BackendProvider } from "./contexts/BackendContext.tsx";

createRoot(document.getElementById("root")!).render(
  <BackendProvider>
    <App />
  </BackendProvider>
);
  