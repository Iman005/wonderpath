import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import fa from "@/i18n/fa";
import LandmarkBackdrop from "@/components/LandmarkBackdrop";
import TopbarProfile from "@/components/TopbarProfile";

export const metadata: Metadata = {
  title: `${fa.appName} — ${fa.tagline}`,
  description: fa.tagline,
  icons: { icon: "/logo.png" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body>
        <a href="#main" className="skip-link">
          رفتن به محتوای اصلی
        </a>
        <LandmarkBackdrop />
        <div className="shell">
          <header className="topbar">
            <Link href="/app" className="brand">
              <img src="/logo.png" alt="" className="brand-logo" />
              <span className="brand-copy">
                <span className="brand-mark">{fa.appName}</span>
                <span className="brand-tagline">{fa.tagline}</span>
              </span>
            </Link>
            <div className="topbar-actions">
              <Link href="/tours" className="topbar-guide">
                {fa.nav.tours}
              </Link>
              <Link href="/guide" className="topbar-guide">
                {fa.nav.guide}
              </Link>
              <TopbarProfile />
            </div>
          </header>
          <main id="main" style={{ flex: 1 }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
