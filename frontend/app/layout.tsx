import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Bloom OS | Login",
  description: "Bloom OS authentication portal",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {/* Realtime provider connects to backend WebSocket and provides subscribe() to pages */}
        {/* Imported lazily as a client component */}
        {/* @ts-ignore */}
        {typeof window !== "undefined" ? (
          // dynamic client-side provider
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          require("@/lib/api/realtime").RealtimeProviderClient
            ? React.createElement(require("@/lib/api/realtime").RealtimeProviderClient, null, children)
            : children
        ) : (
          children
        )}
      </body>
    </html>
  );
}
