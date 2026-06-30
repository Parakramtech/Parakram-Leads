import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import type { Page } from "./types";
import { NavBar } from "./components/NavBar";
import { Footer } from "./components/Footer";
import { WhatsAppFAB } from "./components/WhatsAppFAB";
import HomePage from "./pages/HomePage";
import ServicesPage from "./pages/ServicesPage";
import WorkPage from "./pages/WorkPage";
import ProductsPage from "./pages/ProductsPage";
import StorePage from "./pages/StorePage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import PlayPage from "./pages/PlayPage";
import PrivacyPage from "./pages/PrivacyPage";

function ScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const handle = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0);
    };
    window.addEventListener("scroll", handle, { passive: true });
    return () => window.removeEventListener("scroll", handle);
  }, []);
  return (
    <div className="fixed top-0 left-0 right-0 z-[60] h-[2px]">
      <div className="h-full transition-[width] duration-150 ease-out" style={{ width: `${progress * 100}%`, background: "linear-gradient(90deg,#7a5020,#c9a96e,#f5e4a8)" }} />
    </div>
  );
}

function AppInner() {
  const [page, setPage] = useState<Page>("home");

  const renderPage = () => {
    switch (page) {
      case "home":     return <HomePage setPage={setPage} />;
      case "services": return <ServicesPage setPage={setPage} />;
      case "work":     return <WorkPage />;
      case "products": return <ProductsPage setPage={setPage} />;
      case "store":    return <StorePage setPage={setPage} />;
      case "about":    return <AboutPage setPage={setPage} />;
      case "contact":  return <ContactPage />;
      case "play":     return <PlayPage />;
      case "privacy":  return <PrivacyPage />;
      default:         return <HomePage setPage={setPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground" style={{ fontFamily: "'Instrument Sans', 'Sora', sans-serif" }}>
      <div className="fixed inset-0 pointer-events-none z-[100] opacity-[0.018]" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`, backgroundSize: "180px" }} />
      <ScrollProgress />
      <NavBar current={page} setPage={setPage} />
      <WhatsAppFAB />
      <motion.main key={page} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, ease: [0.2, 0, 0.3, 1] }}>
        {renderPage()}
      </motion.main>
      <Footer setPage={setPage} />
    </div>
  );
}

export default function App() { return <AppInner />; }
