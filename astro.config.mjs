import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://techgeorgii.com",
  vite: {
    preview: {
      allowedHosts: [".up.railway.app"],
    },
  },
});
