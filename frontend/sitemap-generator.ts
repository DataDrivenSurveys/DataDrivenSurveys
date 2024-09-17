import { createWriteStream, existsSync } from 'fs';
import { resolve } from 'path';

import * as dotenv from 'dotenv';
import { SitemapStream, streamToPromise, EnumChangefreq } from 'sitemap';

// Get the NODE_ENV variable (or fallback to 'development')
const environment = process.env.NODE_ENV || 'development';

// Dynamically construct the .env file path based on the environment
const envFilePath = resolve(__dirname, `.env.${environment}`);
const envLocalFilePath = resolve(__dirname, `.env.${environment}.local`);

// Load the environment variables from the corresponding .env file
dotenv.config({ path: envFilePath });

// Check for and load the .env.local file, overriding the baseline values
if (existsSync(envLocalFilePath)) {
  dotenv.config({ path: envLocalFilePath, override: true });
}

// Get the base URL from the environment variable
const baseUrl: string = process.env.REACT_APP_FRONTEND_URL || 'https://www.datadrivensurvey.com';

// Define your routes manually or dynamically
const routes: string[] = [
  '/',
  // '/about',
  // '/contact',
  '/privacy-policy',
  '/terms-of-service',
  '/signup',
  '/signin',
  '/projects',
  '/projects/create',
];

const generateSitemap = async (): Promise<void> => {
  const sitemap = new SitemapStream({ hostname: baseUrl });

  // Write the sitemap to the public directory
  const writeStream = createWriteStream(resolve(__dirname, 'public', 'sitemap.xml'));
  sitemap.pipe(writeStream);

  routes.forEach(route => {
    sitemap.write({
      url: route,
      changefreq: EnumChangefreq.MONTHLY,
      priority: 0.8,
    });
  });

  sitemap.end();
  await streamToPromise(sitemap);

  // eslint-disable-next-line no-console
  console.log('Sitemap generated!');
};

generateSitemap().catch(err => {
  // eslint-disable-next-line no-console
  console.error('Error generating sitemap:', err);
});
