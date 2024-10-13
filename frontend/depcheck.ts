/* eslint-disable no-console */
const depcheck = require('depcheck');

// Define the options to ignore certain dependencies
const options = {
  ignoreMatches: ['depcheck', '@types/next', 'browserslist', 'nodemon'],
  ignorePatterns: ['tsconfig.json'],
};

// Run depcheck
depcheck(process.cwd(), options).then(unused => {
  const { dependencies, devDependencies, missing, using, invalidFiles } = unused;

  // Format and display unused dependencies
  if (dependencies.length) {
    console.log('Unused dependencies');
    dependencies.forEach(dep => {
      console.log(`* ${dep}`);
    });
    console.log();
  }

  // Format and display unused devDependencies
  if (devDependencies.length) {
    console.log('Unused devDependencies');
    devDependencies.forEach(dep => {
      console.log(`* ${dep}`);
    });
    console.log();
  }

  // Format and display missing dependencies
  if (Object.keys(missing).length) {
    console.log('Missing dependencies');
    Object.keys(missing).forEach(dep => {
      console.log(`* ${dep}`);
    });
    console.log();
  }

  // Format and display invalid files
  if (Object.keys(invalidFiles).length) {
    console.log('Invalid files');
    Object.keys(invalidFiles).forEach(file => {
      console.log(`* ${file}`);
    });
    console.log();
  }

  // No issues found
  if (
    !dependencies.length &&
    !devDependencies.length &&
    !Object.keys(missing).length &&
    !Object.keys(invalidFiles).length
  ) {
    console.log('No issues found');
  }
});
