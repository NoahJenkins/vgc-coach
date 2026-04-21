import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const repoBase = "/vgc-coach/";
const customDomainBase = "/";

export default defineConfig({
  plugins: [react()],
  base: process.env.SITE_BASE ?? repoBase,
  define: {
    __DEFAULT_REPO_BASE__: JSON.stringify(repoBase),
    __DEFAULT_CUSTOM_DOMAIN_BASE__: JSON.stringify(customDomainBase),
  },
});
