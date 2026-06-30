"use client";

import SectionLabel from "../components/SectionLabel";

export default function PrivacyPage() {
  const sections = [
    {
      title: "Information We Collect",
      content: "We collect information you provide directly: name, email, phone number, company details when you sign up or contact us. We also collect usage data (pages visited, features used) to improve our services. When you use Parakram VPS, we collect system metrics (CPU, memory, disk usage, uptime) to monitor and maintain your instance.",
    },
    {
      title: "How We Use Your Information",
      content: "We use your information to: provide and maintain our services, send you relevant communications, improve and develop new features, detect and prevent abuse, and comply with legal obligations. We do not sell your personal information to third parties.",
    },
    {
      title: "Data Storage & Security",
      content: "Your data is stored on secure servers with encryption at rest and in transit. We implement industry-standard security measures including SOC 2 compliant practices. You retain ownership of all business data you input into our platform.",
    },
    {
      title: "Third-Party Services",
      content: "We integrate with trusted third-party services including: OpenAI (AI analysis), GitHub (release hosting), Cloudflare (CDN and tunnel infrastructure), Razorpay (payment processing), Twilio (SMS alerts), and WhatsApp (messaging). Each service operates under its own privacy policy.",
    },
    {
      title: "Data Retention",
      content: "We retain your data for as long as your account is active or as needed to provide services. You can request deletion of your data at any time by contacting hello@getparakram.in. We will fulfill deletion requests within 30 days.",
    },
    {
      title: "Your Rights",
      content: "You have the right to: access your personal data, correct inaccurate data, delete your data, restrict processing, data portability, and withdraw consent at any time. To exercise these rights, contact hello@getparakram.in.",
    },
    {
      title: "Cookies",
      content: "We use essential cookies for authentication and security. We do not use tracking cookies or third-party analytics cookies. You can control cookie settings in your browser.",
    },
    {
      title: "Changes to This Policy",
      content: "We may update this privacy policy from time to time. We will notify you of material changes via email or through our platform. Continued use after changes constitutes acceptance of the new policy.",
    },
  ];

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-4xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Privacy</SectionLabel>
          <h1 className="text-3xl md:text-5xl font-bold text-[#e8e6e3] mt-4 mb-4" style={{ fontFamily: "Sora, sans-serif" }}>
            Privacy Statement
          </h1>
          <p className="text-[13px] text-[#555] leading-relaxed max-w-2xl">
            Last updated: June 2026. Parakram Technologies respects your privacy. This statement explains how we collect, use, and protect your information.
          </p>
        </div>

        <div className="space-y-12">
          {sections.map(({ title, content }) => (
            <div key={title}>
              <h2 className="text-lg font-semibold text-[#c9a96e] mb-3" style={{ fontFamily: "Sora, sans-serif" }}>
                {title}
              </h2>
              <p className="text-[13px] text-[#555] leading-relaxed">
                {content}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-16 pt-8 border-t border-white/[0.06]">
          <h2 className="text-lg font-semibold text-[#c9a96e] mb-3" style={{ fontFamily: "Sora, sans-serif" }}>
            Contact
          </h2>
          <p className="text-[13px] text-[#555] leading-relaxed">
            For privacy-related inquiries:{" "}
            <a href="mailto:hello@getparakram.in" className="text-[#c9a96e] hover:text-[#f5e4a8] transition-colors">
              hello@getparakram.in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
