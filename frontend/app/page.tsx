import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import PixelDivider from "@/components/landing/PixelDivider";
import Logos from "@/components/landing/Logos";
import Features from "@/components/landing/Features";
import HowItWorks from "@/components/landing/HowItWorks";
import FinalCTA from "@/components/landing/FinalCTA";
import Footer from "@/components/landing/Footer";

export default function Home() {
  return (
    <main className="flex flex-col w-full bg-[#0A0A0A] pt-[60px]">
      <Navbar />
      <Hero />
      <PixelDivider />
      <Logos />
      <Features />
      <HowItWorks />
      <FinalCTA />
      <Footer />
    </main>
  );
}
