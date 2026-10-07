import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Recon-Bot — Three-Way Matching for Indian Manufacturing MSMEs',
  description:
    'Automate PO ↔ Supplier Invoice ↔ GRN three-way reconciliation with vision AI and deterministic GST, price, and quantity rules. Catch rupee leakage before payment release.',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const theme = localStorage.getItem('theme');
                const supportDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (theme === 'dark' || (!theme && supportDarkMode)) {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-apple-bg-primary-light dark:bg-apple-bg-primary-dark text-apple-text-primary-light dark:text-apple-text-primary-dark font-sans transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
