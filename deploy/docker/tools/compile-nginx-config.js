const fs = require('fs');
const path = require('path');
const nunjucks = require('nunjucks');

nunjucks.configure({ autoescape: true });

const isProduction = process.env.NGINX_ENV === 'production';
const nginxFilePath = path.resolve(__dirname, '../nginx.conf');

const nginxTemplate = String(fs.readFileSync(nginxFilePath));

console.log(nunjucks.renderString(nginxTemplate, { isProduction }));
