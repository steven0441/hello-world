import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'God Dungeon',
  description: 'Your condemned servants, working forever.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="dungeon-bg min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
