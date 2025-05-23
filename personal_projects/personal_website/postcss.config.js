/**
 * PostCSS configuration file
 * 
 * This configuration includes:
 * - tailwindcss: For processing Tailwind CSS directives
 * - autoprefixer: For adding vendor prefixes to CSS rules
 * - postcss-preset-env: For converting modern CSS into something browsers understand
 */

module.exports = {
    plugins: {
      tailwindcss: {},
      autoprefixer: {
        flexbox: 'no-2009',
      },
      'postcss-preset-env': {
        stage: 3,
        features: {
          'custom-properties': false,
        },
      },
    },
  }