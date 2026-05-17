'use client'

import Image from 'next/image'
import { useState } from 'react'
import Link from 'next/link'

interface Product {
  id: string
  name: string
  description: string
  colors: { name: string; filename: string }[]
}

const products: Product[] = [
  {
    id: 'camisetas-hombre',
    name: 'Camiseta Hombre',
    description: 'Camiseta premium de algodón 100% con logo DOS AROS bordado. Diseño minimalista y cómodo para fans de baloncesto.',
    colors: [
      { name: 'Crema', filename: 'camisetas-hombre-crema' },
      { name: 'Marrón Claro', filename: 'camisetas-hombre-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'camisetas-hombre-marron-oscuro' },
      { name: 'Beige', filename: 'camisetas-hombre-beige' },
      { name: 'Negro', filename: 'camisetas-hombre-negro' },
      { name: 'Marrón', filename: 'camisetas-hombre-marron' },
    ],
  },
  {
    id: 'camisetas-mujer',
    name: 'Camiseta Mujer',
    description: 'Camiseta fitted para mujer con corte ergonómico. Perfecta para el día a día con estilo DOS AROS.',
    colors: [
      { name: 'Crema', filename: 'camisetas-mujer-crema' },
      { name: 'Marrón Claro', filename: 'camisetas-mujer-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'camisetas-mujer-marron-oscuro' },
      { name: 'Beige', filename: 'camisetas-mujer-beige' },
      { name: 'Negro', filename: 'camisetas-mujer-negro' },
      { name: 'Marrón', filename: 'camisetas-mujer-marron' },
    ],
  },
  {
    id: 'sudaderas-unisex',
    name: 'Sudadera Unisex',
    description: 'Sudadera cómoda y versátil con diseño unisex. Ideal para entrenamientos y uso casual.',
    colors: [
      { name: 'Crema', filename: 'sudaderas-unisex-crema' },
      { name: 'Marrón Claro', filename: 'sudaderas-unisex-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'sudaderas-unisex-marron-oscuro' },
      { name: 'Beige', filename: 'sudaderas-unisex-beige' },
      { name: 'Negro', filename: 'sudaderas-unisex-negro' },
      { name: 'Marrón', filename: 'sudaderas-unisex-marron' },
    ],
  },
  {
    id: 'gorras-unisex',
    name: 'Gorra Unisex',
    description: 'Gorra ajustable con logo DOS AROS bordado. Material de calidad con protección UV.',
    colors: [
      { name: 'Crema', filename: 'gorras-unisex-crema' },
      { name: 'Marrón Claro', filename: 'gorras-unisex-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'gorras-unisex-marron-oscuro' },
      { name: 'Beige', filename: 'gorras-unisex-beige' },
      { name: 'Negro', filename: 'gorras-unisex-negro' },
      { name: 'Marrón', filename: 'gorras-unisex-marron' },
    ],
  },
  {
    id: 'totebags-unisex',
    name: 'Totebag Unisex',
    description: 'Bolsa totebag espaciosa y resistente. Perfecta para llevar tus cosas con estilo DOS AROS.',
    colors: [
      { name: 'Crema', filename: 'totebags-unisex-crema' },
      { name: 'Marrón Claro', filename: 'totebags-unisex-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'totebags-unisex-marron-oscuro' },
      { name: 'Beige', filename: 'totebags-unisex-beige' },
      { name: 'Negro', filename: 'totebags-unisex-negro' },
      { name: 'Marrón', filename: 'totebags-unisex-marron' },
    ],
  },
]

export default function ProductCatalog() {
  const [selectedProductId, setSelectedProductId] = useState<string>('camisetas-hombre')

  const selected = products.find(p => p.id === selectedProductId)!

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h2 className="text-4xl md:text-5xl font-heading font-bold text-dos-blue dark:text-dos-white mb-4">
          Catálogo de Productos
        </h2>
        <p className="text-dos-gray text-lg max-w-2xl mx-auto">
          Descubre nuestra colección de merchandising premium. Diseñado para los verdaderos apasionados del baloncesto.
        </p>
      </div>

      {/* Product Selector Tabs */}
      <div className="flex flex-wrap gap-2 mb-8 justify-center">
        {products.map((product) => (
          <button
            key={product.id}
            onClick={() => setSelectedProductId(product.id)}
            className={`px-4 py-2 rounded-lg font-bold transition-all ${
              selectedProductId === product.id
                ? 'bg-dos-orange text-dos-white'
                : 'bg-dos-gray/10 text-dos-blue dark:bg-dos-magenta/10 dark:text-dos-white hover:bg-dos-orange/20'
            }`}
          >
            {product.name}
          </button>
        ))}
      </div>

      {/* Product Info */}
      <div className="bg-dos-blue/5 dark:bg-dos-blue-dark/50 rounded-lg p-6 mb-8 border border-dos-gray/20 dark:border-dos-magenta/20">
        <h3 className="text-2xl font-heading font-bold text-dos-blue dark:text-dos-white mb-2">
          {selected.name}
        </h3>
        <p className="text-dos-gray dark:text-dos-gray">
          {selected.description}
        </p>
      </div>

      {/* Product Images Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
        {selected.colors.map((color) => (
          <div key={color.filename} className="group">
            <div className="relative w-full aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-900 border border-dos-gray/20 dark:border-dos-magenta/20 hover:border-dos-orange transition-all">
              <Image
                src={`/productos/${color.filename}.png`}
                alt={`${selected.name} - ${color.name}`}
                fill
                className="object-cover group-hover:scale-105 transition-transform"
              />
            </div>
            <p className="text-center text-sm font-medium text-dos-gray dark:text-dos-gray mt-2 group-hover:text-dos-orange transition-colors">
              {color.name}
            </p>
          </div>
        ))}
      </div>

      {/* CTA Section */}
      <div className="bg-dos-orange/10 dark:bg-dos-orange/5 rounded-lg p-8 text-center border border-dos-orange/20">
        <h3 className="text-2xl font-heading font-bold text-dos-blue dark:text-dos-white mb-4">
          Listo para comprar
        </h3>
        <p className="text-dos-gray dark:text-dos-gray mb-6">
          Elige tu color favorito de {selected.name.toLowerCase()} y ponte en contacto con nosotros para hacer tu pedido.
        </p>
        <Link
          href={`/contact?product=${encodeURIComponent(selected.name)}`}
          className="inline-block bg-dos-orange hover:bg-dos-orange-dark text-dos-white font-bold py-3 px-8 rounded-lg transition-colors"
        >
          Comprar Ahora
        </Link>
      </div>
    </div>
  )
}
