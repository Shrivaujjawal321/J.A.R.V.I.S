import type { Metadata, Viewport } from 'next';
import { fraunces, geistSans, geistMono } from '@/lib/fonts';
import { SmoothScroller } from '@/components/SmoothScroller';
import { CustomCursor } from '@/components/CustomCursor';
import './globals.css';

export const metadata: Metadata = {
  title: 'The Corner Pocket — Premium Snooker Club, Mumbai',
  description:
    'Mumbai\'s finest snooker destination. Tournament-grade tables, elite membership, professional coaching, and a bar worth staying for. Where the city racks up after dark.',
  keywords: [
    'snooker club mumbai',
    'premium snooker',
    'snooker membership',
    'billiards mumbai',
    'pool club mumbai',
    'snooker coaching',
  ],
  authors: [{ name: 'The Corner Pocket' }],
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://cornerpocket.in',
    siteName: 'The Corner Pocket',
    title: 'The Corner Pocket — Premium Snooker Club, Mumbai',
    description: "Mumbai's finest snooker destination. Where the city racks up after dark.",
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'The Corner Pocket — Premium Snooker Club',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'The Corner Pocket — Premium Snooker Club, Mumbai',
    description: "Mumbai's finest snooker destination.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: '#0a0d0a',
  width: 'device-width',
  initialScale: 1,
};

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SportsActivityLocation',
  name: 'The Corner Pocket',
  description: "Mumbai's premium snooker club",
  address: {
    '@type': 'PostalAddress',
    streetAddress: '42, Linking Road',
    addressLocality: 'Bandra West',
    addressRegion: 'Maharashtra',
    postalCode: '400050',
    addressCountry: 'IN',
  },
  telephone: '+91-22-4567-8900',
  openingHours: ['Mo-Su 12:00-02:00'],
  priceRange: '₹₹₹',
  sport: 'Snooker',
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${geistSans.variable} ${geistMono.variable}`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://images.unsplash.com" />
      </head>
      <body className="bg-bg text-cream font-body">
        <SmoothScroller>
          <CustomCursor />
          {children}
        </SmoothScroller>
      </body>
    </html>
  );
}
