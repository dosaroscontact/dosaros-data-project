import Navbar from '@/components/Navbar'
import StickyTicker from '@/components/StickyTicker'
import Hero from '@/components/Hero'
import Highlights from '@/components/Highlights'
import Products from '@/components/Products'
import QueryBox from '@/components/QueryBox'
import Newsletter from '@/components/Newsletter'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main id="main-content">
      <Navbar />
      <StickyTicker />
      <Hero />
      <Highlights />
      <Products />
      <QueryBox />
      <Newsletter />
      <Footer />
    </main>
  )
}
