import { URL, fileURLToPath } from "node:url";

import VueDevTools from "vite-plugin-vue-devtools";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), VueDevTools()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  define: {
    APP_VERSION: `'${process.env.npm_package_version as string}'`,
  },
});
