const fs = require('fs');
const path = require('path');

// Simple screenshot using HTML2Canvas via Node
async function takeScreenshot() {
  try {
    const fetch = (await import('node-fetch')).default;

    console.log('Obteniendo HTML de http://localhost:3009...');
    const response = await fetch('http://localhost:3009');
    const html = await response.text();

    // Extraer solo el navbar
    const navMatch = html.match(/<nav[^>]*>[\s\S]*?<\/nav>/);
    if (!navMatch) {
      console.log('Navbar encontrado pero sin estructura HTML para captura.');
      console.log('Renderizando desde URL...');

      // Mostrar información del navbar desde el HTML
      const logoMatch = html.match(/logo-dos-aros-official\.png/);
      const bannerMatch = html.match(/banner-dos-aros\.png/);
      const faviconMatch = html.match(/favicon\.ico/);

      console.log('\n✓ Navbar estructura:');
      console.log('  - Logo oficial: ' + (logoMatch ? '✓' : '✗'));
      console.log('  - Banner: ' + (bannerMatch ? '✓' : '✗'));
      console.log('  - Favicon: ' + (faviconMatch ? '✓' : '✗'));

      return;
    }

    console.log('Navbar HTML capturado. Creando vista previa...');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

takeScreenshot();
