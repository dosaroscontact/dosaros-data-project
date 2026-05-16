import Navbar from '@/components/Navbar'
import ContactForm from '@/components/ContactForm'
import Footer from '@/components/Footer'

export const metadata = {
  title: 'Contacto — DOS AROS',
  description: 'Ponte en contacto con nosotros. Estamos en fase de lanzamiento y pronto nos comunicaremos contigo.',
}

export default function ContactPage() {
  return (
    <main id="main-content">
      <Navbar />
      <div className="pt-20 sm:pt-24">
        <ContactForm />
      </div>
      <Footer />
    </main>
  )
}
