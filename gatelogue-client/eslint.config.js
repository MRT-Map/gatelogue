// @ts-check

import globals from "globals";
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import prettierConfig from "eslint-config-prettier";
import tseslint from "typescript-eslint";
import vueParser from "vue-eslint-parser";

export default tseslint.config(
  pluginJs.configs.all,
  ...tseslint.configs.strict,
  ...tseslint.configs.stylistic,
  ...pluginVue.configs["flat/essential"],
  ...pluginVue.configs["flat/recommended"],
  {
    languageOptions: {
      sourceType: "module",
      globals: globals.browser,
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
      },
    },
    rules: {
      "@typescript-eslint/ban-ts-comment": "off",
      "@typescript-eslint/no-non-null-asserted-optional-chain": "off",
      "@typescript-eslint/no-non-null-assertion": "off",
      "capitalized-comments": "off",
      "id-length": "off",
      "new-cap": "off",
      "no-magic-numbers": "off",
      "no-ternary": "off",
      "no-undefined": "off",
      "no-useless-assignment": "off",
      "one-var": "off",
      radix: "off",
      "sort-keys": "off",
      "sort-imports": "off",
      "vue/multi-word-component-names": "off",
    },
  },
  prettierConfig,
);
