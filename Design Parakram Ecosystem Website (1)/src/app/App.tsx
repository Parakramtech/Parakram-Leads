import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import type { Page } from "./types";
import { NavBar } from "./components/NavBar";
import { Footer } from "./components/Footer";
import { WhatsAppFAB } from "./components/WhatsAppFAB";
import HomePage from "./pages/HomePage";
import ServicesPage from "./pages/ServicesPage";
import WorkPage from "./pages/WorkPage";
import ProductsPage from "./pages/ProductsPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import PlayPage from "./pages/PlayPage";

function AppInner() {
  const [page, setPage] = useState<Page>("home");

  const renderPage = () => {
    switch (page) {
      case "home":     return <HomePage setPage={setPage} />;
      case "services": return <ServicesPage setPage={setPage} />;
      case "work":     return <WorkPage />;
      case "products": return <ProductsPage setPage={setPage} />;
      case "about":    return <AboutPage setPage={setPage} />;
      case "contact":  return <ContactPage />;
      case "play":     return <PlayPage />;
      default:         return <HomePage setPage={setPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground" style={{ fontFamily: "'Instrument Sans', 'Sora', sans-serif" }}>
      <div className="fixed inset-0 pointer-events-none z-[100] opacity-[0.018]" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`, backgroundSize: "180px" }} />
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
