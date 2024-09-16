import { existsSync, writeFileSync } from 'fs';
import { resolve } from 'path';

import * as dotenv from 'dotenv';

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

// Get the base URL for your site from the environment variables
const baseUrl: string = process.env.REACT_APP_FRONTEND_URL || 'https://www.datadrivensurvey.com';
const domain: string = baseUrl.replace(/^https?:\/\//, '');

// Create the content for the robots.txt file
const robotsContent = `# https://www.robotstxt.org/robotstxt.html
User-agent: *
Sitemap: ${baseUrl}/sitemap.xml
Allow: /projects
Disallow: http://${domain}
Disallow: /projects/create
Disallow: /projects/
Disallow: /dist
Disallow: /survey_platform`;

// Write the robots.txt file to the public directory
writeFileSync(resolve(__dirname, 'public', 'robots.txt'), robotsContent);

// eslint-disable-next-line no-console
console.log('robots.txt generated!');
