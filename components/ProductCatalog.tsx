'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import { motion } from 'framer-motion'

interface ProductCategory {
  id: string
  name: string
  badge: string
  description: string
  items: { name: string; filename: string }[]
}

const products: ProductCategory[] = [
  {
    id: 'camisetas-hombre',
    name: 'Camiseta Hombre',
    badge: 'Camiseta',
    description: 'Camiseta premium de algodón 100% con logo DOS AROS. Diseño minimalista y cómodo para fans de baloncesto.',
    items: [
      { name: 'Crema', filename: 'camisetas-hombre-crema' },
      { name: 'Blanca', filename: 'camisetas-hombre-blanca' },
      { name: 'Marrón Claro', filename: 'camisetas-hombre-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'camisetas-hombre-marron-oscuro' },
      { name: 'Verde', filename: 'camisetas-hombre-verde' },
    ],
  },
  {
    id: 'camisetas-mujer',
    name: 'Camiseta Mujer',
    badge: 'Camiseta',
    description: 'Camiseta fitted para mujer con corte ergonómico. Perfecta para el día a día con estilo DOS AROS.',
    items: [
      { name: 'Crema', filename: 'camisetas-mujer-crema' },
      { name: 'Marrón Claro', filename: 'camisetas-mujer-marron-claro' },
      { name: 'Marrón Oscuro', filename: 'camisetas-mujer-marron-oscuro' },
      { name: 'Verde', filename: 'camisetas-mujer-verde' },
      { name: 'Negro', filename: 'camisetas-mujer-negro' },
    ],
  },
  {
    id: 'sudaderas-unisex',
    name: 'Sudadera Unisex',
    badge: 'Sudadera',
    description: 'Sudadera cómoda y versátil con diseño unisex. Ideal para entrenamientos y uso casual.',
    items: [
      { name: 'Crema', filename: 'sudaderas-unisex-crema' },
      { name: 'Crema Simple', filename: 'sudaderas-unisex-crema-simple' },
      { name: 'Marrón', filename: 'sudaderas-unisex-marron' },
      { name: 'Verde', filename: 'sudaderas-unisex-verde' },
    ],
  },
  {
    id: 'gorras-unisex',
    name: 'Gorra Unisex',
    badge: 'Gorra',
    description: 'Gorra ajustable con logo DOS AROS bordado. Material de calidad con protección UV.',
    items: [
      { name: 'Crema', filename: 'gorras-unisex-crema' },
      { name: 'Beige', filename: 'gorras-unisex-beige' },
      { name: 'Marrón Claro', filename: 'gorras-unisex-marron-claro' },
      { name: 'Marrón', filename: 'gorras-unisex-marron' },
      { name: 'Marrón Oscuro', filename: 'gorras-unisex-marron-oscuro' },
      { name: 'Negro', filename: 'gorras-unisex-negro' },
    ],
  },
  {
    id: 'totebags-unisex',
    name: 'Totebag Unisex',
    badge: 'Totebag',
    description: 'Bolsa totebag espaciosa y resistente. Perfecta para llevar tus cosas con estilo DOS AROS.',
    items: [
      { name: 'Crema', filename: 'totebags-unisex-crema' },
      { name: 'Beige', filename: 'totebags-unisex-beige' },
      { name: 'Marrón Claro', filename: 'totebags-unisex-marron-claro' },
      { name: 'Marrón', filename: 'totebags-unisex-marron' },
      { name: 'Marrón Oscuro', filename: 'totebags-unisex-marron-oscuro' },
      { name: 'Verde', filename: 'totebags-unisex-verde' },
    ],
  },
  {
    id: 'accesorios',
    name: 'Accesorios',
    badge: 'Accesorio',
    description: 'Complementos DOS AROS para llevar tu pasión por el baloncesto contigo, donde sea que vayas.',
    items: [
      { name: 'Bandana', filename: 'bandana' },
      { name: 'Bucket Hat Verde', filename: 'bucket-hat-verde' },
      { name: 'Botella', filename: 'botella' },
      { name: 'Taza', filename: 'taza' },
      { name: 'Cuaderno', filename: 'cuaderno' },
      { name: 'Llavero', filename: 'llavero' },
      { name: 'Poster', filename: 'poster' },
    ],
  },
]

export default function ProductCatalog() {
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('camisetas-hombre')

  const selected = products.find(p => p.id === selectedCategoryId)!
  const isAccesorios = selected.id === 'accesorios'

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.08 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  }

  return (
    <section className="w-full py-16 sm:py-20 px-4 sm:px-6 bg-gradient-to-br from-dos-blue/5 to-dos-magenta/5">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue dark:text-dos-white mb-3">
            Catálogo de Productos
          </h1>
          <p className="text-dos-gray-dark dark:text-dos-gray text-base sm:text-lg max-w-2xl mx-auto">
            Descubre nuestra colección de merchandising premium. Diseñado para los verdaderos apasionados del baloncesto.
          </p>
        </motion.div>

        {/* Category Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          viewport={{ once: true }}
          className="flex flex-wrap gap-2 mb-8 justify-center"
        >
          {products.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategoryId(category.id)}
              className={`px-4 py-2 rounded-lg font-heading font-bold text-sm transition-all ${
                selectedCategoryId === category.id
                  ? 'bg-dos-orange text-dos-blue'
                  : 'bg-dos-white dark:bg-dos-blue/30 text-dos-blue dark:text-dos-white border-2 border-dos-gray/20 dark:border-dos-magenta/20 hover:border-dos-orange/50'
              }`}
            >
              {category.name}
            </button>
          ))}
        </motion.div>

        {/* Category Description */}
        <motion.p
          key={selected.id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="text-center text-dos-gray-dark dark:text-dos-gray mb-10 max-w-2xl mx-auto italic"
        >
          {selected.description}
        </motion.p>

        {/* Products Grid — Same format as Home */}
        <motion.div
          key={`grid-${selected.id}`}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
        >
          {selected.items.map((item) => {
            const productName = isAccesorios
              ? `${item.name} DOS AROS`
              : `${selected.name} ${item.name}`

            return (
              <motion.div
                key={item.filename}
                variants={itemVariants}
                className="group cursor-pointer"
              >
                <div className="relative overflow-hidden rounded-xl border-2 border-dos-gray/20 dark:border-dos-magenta/20 bg-dos-white dark:bg-dos-blue/30 hover:border-dos-orange/50 transition-all duration-300 shadow-md hover:shadow-lg">
                  {/* Product Image */}
                  <div className="relative w-full aspect-square bg-gradient-to-br from-dos-gray/10 to-dos-magenta/10 overflow-hidden">
                    <Image
                      src={`/productos/${item.filename}.png`}
                      alt={productName}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    />
                    {/* Category badge */}
                    <div className="absolute top-3 right-3 bg-dos-orange-dark text-dos-white px-3 py-1 rounded-full text-xs font-heading font-bold">
                      {selected.badge}
                    </div>
                  </div>

                  {/* Product Info */}
                  <div className="p-4 sm:p-5">
                    <h3 className="text-lg font-heading font-bold text-dos-blue dark:text-dos-white mb-2 group-hover:text-dos-orange transition-colors">
                      {productName}
                    </h3>
                    {!isAccesorios && (
                      <p className="text-sm text-dos-gray-dark dark:text-dos-gray mb-4">
                        Color: <span className="font-semibold">{item.name}</span>
                      </p>
                    )}
                    {isAccesorios && (
                      <p className="text-sm text-dos-gray-dark dark:text-dos-gray mb-4">
                        Producto exclusivo DOS AROS
                      </p>
                    )}
                    <Link
                      href={`/contact?product=${encodeURIComponent(productName)}`}
                      className="block w-full px-4 py-2.5 bg-dos-orange hover:opacity-90 text-dos-blue font-heading font-bold rounded-lg transition-opacity duration-300 active:scale-95 text-sm text-center"
                      aria-label={`Consultar disponibilidad de ${productName}`}
                    >
                      Ver disponibilidad
                    </Link>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
