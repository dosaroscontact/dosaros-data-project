const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function generateFavicon() {
  try {
    const inputPath = path.join(__dirname, '../public/logo-dos-aros-official.png');
    const outputPath = path.join(__dirname, '../public/favicon.ico');

    console.log('Generando favicon...');

    // Crear favicon de 32x32 en ICO format
    await sharp(inputPath)
      .resize(32, 32, {
        fit: 'cover',
        position: 'center'
      })
      .toFile(outputPath);

    console.log('✓ Favicon generado correctamente en:', outputPath);
  } catch (error) {
    console.error('Error generando favicon:', error.message);
    process.exit(1);
  }
}

generateFavicon();
