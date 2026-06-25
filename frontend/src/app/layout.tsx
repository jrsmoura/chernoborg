import type { Metadata } from 'next';
import { Source_Sans_3 } from 'next/font/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';

const sourceSans = Source_Sans_3({
  subsets: ['latin'],
  weight: ['300', '400', '600', '700'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'IA IESB',
  description: 'Conte comigo para sanar as suas dúvidas.',
  icons: { icon: '/favicon.ico' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={sourceSans.className}>
      <body>{children}</body>
    </html>
  );
}
