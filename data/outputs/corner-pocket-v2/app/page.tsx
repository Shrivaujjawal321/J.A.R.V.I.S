import { Loader } from '@/components/Loader';
import { Nav } from '@/components/Nav';
import { Hero } from '@/components/hero/Hero';
import { About } from '@/components/About';
import { TablesHorizontal } from '@/components/TablesHorizontal';
import { Membership } from '@/components/Membership';
import { Coaching } from '@/components/Coaching';
import { Events } from '@/components/Events';
import { Gallery } from '@/components/Gallery';
import { Booking } from '@/components/Booking';
import { Contact } from '@/components/Contact';
import { Footer } from '@/components/Footer';

// This is a Server Component. All animation layers inside each section
// are Client Components that self-hydrate. This keeps the RSC shell light
// and lets Next.js stream the static structure instantly.
export default function HomePage() {
  return (
    <>
      <Loader />
      <Nav />
      <main id="main-content">
        <Hero />
        <About />
        <TablesHorizontal />
        <Membership />
        <Coaching />
        <Events />
        <Gallery />
        <Booking />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
