'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'

interface Product {
  id: string
  name: string
  image: string
  category: 'Camiseta' | 'Sudadera'
  color: string
}

const PRODUCTS: Product[] = [
  {
    id: '1',
    name: 'Camiseta DOS AROS Beige',
    image: '/productos/camiseta-beige.png',
    category: 'Camiseta',
    color: 'Beige',
  },
  {
    id: '2',
    name: 'Camiseta DOS AROS Verde Tierra',
    image: '/productos/camiseta-verde.png',
    category: 'Camiseta',
    color: 'Verde Tierra',
  },
  {
    id: '3',
    name: 'Camiseta DOS AROS Gris Tierra',
    image: '/productos/camiseta-gris.png',
    category: 'Camiseta',
    color: 'Gris Tierra',
  },
  {
    id: '4',
    name: 'Sudadera DOS AROS Beige',
    image: '/productos/sudadera-beige.png',
    category: 'Sudadera',
    color: 'Beige',
  },
  {
    id: '5',
    name: 'Sudadera DOS AROS Clásica',
    image: '/productos/sudadera-dos-lados.png',
    category: 'Sudadera',
    color: 'Multicolor',
  },
]

export default function Products() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  }

  return (
    <section className="w-full py-16 sm:py-20 px-4 sm:px-6 bg-gradient-to-br from-dos-blue/5 to-dos-magenta/5">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue mb-3">
            Nuestros Primeros Productos
          </h2>
          <p className="text-dos-gray-dark text-base sm:text-lg max-w-2xl mx-auto">
            Lleva el espíritu de DOS AROS contigo. Camisetas y sudaderas premium con diseño exclusivo.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
        >
          {PRODUCTS.map((product) => (
            <motion.div
              key={product.id}
              variants={itemVariants}
              className="group cursor-pointer"
            >
              <div className="relative overflow-hidden rounded-xl border-2 border-dos-gray/20 dark:border-dos-magenta/20 bg-dos-white dark:bg-dos-blue/30 hover:border-dos-orange/50 transition-all duration-300 shadow-md hover:shadow-lg">
                {/* Product Image */}
                <div className="relative w-full aspect-square bg-gradient-to-br from-dos-gray/10 to-dos-magenta/10 overflow-hidden">
                  <Image
                    src={product.image}
                    alt={product.name}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  />
                  {/* Category badge */}
                  <div className="absolute top-3 right-3 bg-dos-orange-dark text-dos-white px-3 py-1 rounded-full text-xs font-heading font-bold">
                    {product.category}
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-4 sm:p-5">
                  <h3 className="text-lg font-heading font-bold text-dos-blue dark:text-dos-white mb-2 group-hover:text-dos-orange transition-colors">
                    {product.name}
                  </h3>
                  <p className="text-sm text-dos-gray-dark dark:text-dos-gray mb-4">
                    Color: <span className="font-semibold">{product.color}</span>
                  </p>
                  <button
                    className="w-full px-4 py-2.5 bg-dos-orange hover:opacity-90 text-dos-blue font-heading font-bold rounded-lg transition-opacity duration-300 active:scale-95 text-sm"
                    aria-label={`Comprar ${product.name}`}
                  >
                    Ver disponibilidad
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <a
            href="#"
            className="inline-flex items-center gap-2 px-8 py-3 sm:py-4 bg-dos-blue hover:bg-dos-blue/90 text-dos-white font-heading font-bold rounded-lg transition-colors duration-300 active:scale-95 min-h-[48px]"
          >
            Explorar toda la colección
          </a>
        </motion.div>
      </div>
    </section>
  )
}
