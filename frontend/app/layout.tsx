import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import { ConstellationBg } from "@/components/ConstellationBg";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "LiftLens",
  description: "Upload your workout video and get instant AI-powered form feedback.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased`}
      >
        <ConstellationBg />
        {children}
      </body>
    </html>
  );
}
