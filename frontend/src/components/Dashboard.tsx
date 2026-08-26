"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { X, ChevronRight, Download } from "lucide-react";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export default function Dashboard() {
  const [stats, setStats] = useState({ total_clusters: 0, total_insights_processed: 0 });
  const [clusters, setClusters] = useState<any[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<any>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("Dashboard");

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setSearchResult(null);
    try {
      const res = await axios.post(`${API_BASE}/query`, { query: searchQuery });
      setSearchResult(res.data);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResult({ answer: "Search failed. Please check your backend connection and ensure GROQ_API_KEY is set.", sources: [] });
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, clustersRes] = await Promise.all([
          axios.get(`${API_BASE}/stats`),
          axios.get(`${API_BASE}/clusters`)
        ]);
        setStats(statsRes.data);
        setClusters(clustersRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const openCluster = async (cluster: any) => {
    setSelectedCluster(cluster);
    setInsights([]);
    try {
      const res = await axios.get(`${API_BASE}/insights/${cluster.cluster_id}`);
      setInsights(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const generatePDFReport = () => {
    const doc = new jsPDF();
    
    // Title
    doc.setFontSize(22);
    doc.setTextColor(20, 184, 166); // primary color
    doc.text("Discover The Unmet", 14, 20);
    
    // Subtitle
    doc.setFontSize(14);
    doc.setTextColor(100);
    doc.text("AI-Powered Friction Analysis Report", 14, 30);
    
    // Timestamp
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 38);
    
    // Stats Section
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Platform Trends:", 14, 50);
    doc.setFontSize(11);
    doc.text(`Total Feedback Processed: ${stats.total_insights_processed}`, 14, 58);
    doc.text(`Active Problem Clusters: ${stats.total_clusters}`, 14, 64);
    
    let yPos = 80;
    
    // Search Query Section
    if (searchQuery && searchResult) {
      doc.setFontSize(14);
      doc.text("Latest AI Query & Synthesis:", 14, yPos);
      yPos += 8;
      
      doc.setFontSize(11);
      doc.setTextColor(50);
      const splitQuery = doc.splitTextToSize(`Query: "${searchQuery}"`, 180);
      doc.text(splitQuery, 14, yPos);
      yPos += (splitQuery.length * 6) + 4;
      
      const splitAnswer = doc.splitTextToSize(searchResult.answer, 180);
      doc.text(splitAnswer, 14, yPos);
      yPos += (splitAnswer.length * 6) + 10;
    }
    
    // Add page if needed before table
    if (yPos > 250) {
      doc.addPage();
      yPos = 20;
    }
    
    // Cluster Table
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Opportunity Score Ranking (Cluster Breakdown):", 14, yPos);
    
    const tableData = clusters.map(c => [
      c.cluster_name,
      c.prevalence.toString(),
      c.opportunity_score.toFixed(1)
    ]);
    
    autoTable(doc, {
      startY: yPos + 6,
      head: [['Cluster Name', 'Volume', 'Opportunity Score']],
      body: tableData,
      theme: 'grid',
      headStyles: { fillColor: [20, 184, 166] }
    });
    
    doc.save("AJIO_Discovery_Report.pdf");
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-background text-on-surface">Loading Discovery Engine...</div>;
  }

  return (
    <div className="flex flex-col md:flex-row min-h-screen antialiased bg-background">
      
      {/* TopNavBar (Mobile Only) */}
      <nav className="flex justify-between items-center w-full px-4 py-4 max-w-container-max-width mx-auto bg-white/5 backdrop-blur-md sticky top-0 md:hidden z-50 shadow-[0_4px_20px_rgba(20,184,166,0.15)]">
        <div className="font-display-lg-mobile text-2xl tracking-tighter text-primary bg-clip-text">AJIO Discovery</div>
        <div className="flex gap-4">
          <button className="text-primary hover:bg-white/10 transition-all duration-300 rounded-full p-2 scale-102 active:scale-95">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="text-primary hover:bg-white/10 transition-all duration-300 rounded-full p-2 scale-102 active:scale-95">
            <span className="material-symbols-outlined">settings</span>
          </button>
        </div>
      </nav>

      {/* SideNavBar (Desktop) */}
      <aside className="hidden md:flex flex-col h-screen w-80 fixed left-0 top-0 bg-surface border-r border-white/10 z-40 py-6">
        <div className="px-6 mb-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full border border-white/10 bg-primary/20 flex items-center justify-center text-primary font-bold">A</div>
          <div className="font-body-sm text-sm text-on-surface">AJIO Admin</div>
        </div>
        <div className="px-6 mb-8">
          <h1 className="font-headline-md text-2xl font-semibold text-primary truncate">AJIO Discovery Engine</h1>
          <p className="font-body-sm text-sm text-on-surface-variant mt-1">Premium Curator v2.1</p>
        </div>
        <nav className="flex-1 px-2 space-y-2">
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Dashboard"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Dashboard" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">dashboard</span>
            Dashboard
          </a>
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Trends"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Trends" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">trending_up</span>
            Trends
          </a>
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Inventory"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Inventory" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">inventory_2</span>
            Inventory
          </a>
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Feedback"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Feedback" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">comment</span>
            Feedback
          </a>
          <div className="pt-4 px-2">
            <button onClick={generatePDFReport} className="w-full bg-primary-container text-on-primary-container py-3 rounded-lg font-label-bold text-sm hover:bg-primary-fixed transition-colors flex items-center justify-center gap-2 shadow-sm">
              <span className="material-symbols-outlined text-sm">download</span>
              Generate Report
            </button>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-80 p-6 md:p-10 w-full max-w-container-max-width mx-auto">
        
        {activeTab === "Dashboard" && (
          <>
            {/* Header & Semantic Search */}
            <header className="mb-12 flex flex-col gap-6">
          <div>
            <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
              Discover The Unmet
            </h1>
            <p className="font-body-lg text-lg text-on-surface-variant mt-2">
              AI-Powered Friction Analysis From Multi-Channel User Feedback.
            </p>
          </div>

          {/* Semantic Search Bar */}
          <div className="relative max-w-3xl">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-on-surface-variant">search</span>
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ask the AI (e.g., 'Why are users abandoning their carts?')"
              className="w-full pl-12 pr-24 py-4 bg-white/5 border border-white/10 rounded-xl text-on-surface placeholder-on-surface-variant focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all"
            />
            <button 
              onClick={handleSearch}
              disabled={isSearching || !searchQuery}
              className={`absolute inset-y-2 right-2 px-6 bg-primary-container text-on-primary-container rounded-lg font-label-bold text-sm hover:bg-primary-fixed transition-colors disabled:opacity-50 flex items-center gap-2 ${isSearching ? 'animate-glow-pulse' : ''}`}
            >
              {isSearching ? <span className="material-symbols-outlined animate-spin text-sm">sync</span> : 'Ask AI'}
            </button>
          </div>

          {/* Suggested Queries */}
          <div className="mb-8">
            <h4 className="text-xs font-label-bold text-on-surface-variant uppercase mb-3 ml-1">Suggested PM Queries</h4>
            <div className="flex flex-wrap gap-2">
              {[
                "Why do users add fashion products to their wishlist?",
                "What prevents wishlisted products from eventually being purchased?",
                "What uncertainties remain after users have identified a product they like?",
                "What causes users to postpone a purchase?",
                "How do users compare multiple shortlisted products?",
                "What information do users seek outside Myntra/AJIO before purchasing?",
                "What role do fit, size, styling, price, reviews, occasion and social validation play?",
                "When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?",
                "How do these behaviors differ across user segments?",
                "What unmet needs emerge consistently across user conversations?"
              ].map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSearchQuery(query);
                    // We don't auto-trigger search to allow the user to review it first, 
                    // but we could. For now, let's just populate the bar.
                  }}
                  className="text-xs bg-surface-variant/50 hover:bg-primary-container hover:text-on-primary-container text-on-surface-variant py-1.5 px-3 rounded-full transition-colors border border-outline-variant/30 text-left"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>

          {/* AI Search Result Panel */}
          {searchResult && (
            <div className="max-w-3xl glass-panel p-6 rounded-xl border border-primary-container/30 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-primary-container"></div>
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-headline-sm text-lg font-semibold text-primary-container flex items-center gap-2">
                  <span className="material-symbols-outlined">auto_awesome</span> AI Synthesis
                </h3>
                <button onClick={() => setSearchResult(null)} className="text-on-surface-variant hover:text-on-surface">
                  <X size={20} />
                </button>
              </div>
              <div className="text-on-surface text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                {searchResult.answer.split('\n').map((line: string, i: number) => (
                  <React.Fragment key={i}>
                    {line.split(/(\*\*.*?\*\*)/).map((part: string, j: number) => {
                      if (part.startsWith('**') && part.endsWith('**')) {
                        const cleanTitle = part.replace(/\*\*/g, '').trim().replace(/:$/, '');
                        return (
                          <div key={j} className="text-primary font-extrabold text-lg tracking-wide mt-2 block w-full border-b border-primary/20 pb-0.5">
                            {cleanTitle}
                          </div>
                        );
                      }
                      return <span key={j}>{part}</span>;
                    })}
                    {i < searchResult.answer.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
              
              <h4 className="text-xs font-label-bold text-on-surface-variant uppercase mb-3">Sources Cited ({searchResult.sources.length})</h4>
              <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-2 scrollbar-hide">
                {searchResult.sources.map((src: any, idx: number) => (
                  <div key={idx} className="p-3 bg-black/40 rounded-lg border border-white/5 text-xs text-on-surface-variant flex items-start gap-3">
                    <span className="text-primary-container font-mono opacity-50">[{idx+1}]</span>
                    <span>"{src.problem_statement}"</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </header>

          </>
        )}
        
        {activeTab === "Trends" && (
          <>
            <header className="mb-12 flex flex-col gap-6">
              <div>
                <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
                  Platform Trends
                </h1>
                <p className="font-body-lg text-lg text-on-surface-variant mt-2">
                  High-level performance and opportunity metrics.
                </p>
              </div>
            </header>

            {/* KPI Cards */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Card 1 */}
          <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 group transition-transform duration-300 hover:scale-[1.02] hover:border-primary-container/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-primary-container/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex justify-between items-start relative z-10">
              <h3 className="font-headline-sm text-xl font-semibold text-on-surface">Total Feedback Processed</h3>
              <span className="material-symbols-outlined text-primary-container bg-primary-container/10 p-2 rounded-lg">group</span>
            </div>
            <div className="font-display-lg text-4xl font-bold text-on-surface relative z-10">{stats.total_insights_processed}</div>
          </div>
          
          {/* Card 2 */}
          <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 group transition-transform duration-300 hover:scale-[1.02] hover:border-tertiary-container/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-tertiary-container/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex justify-between items-start relative z-10">
              <h3 className="font-headline-sm text-xl font-semibold text-on-surface">Active Problem Clusters</h3>
              <span className="material-symbols-outlined text-tertiary-container bg-tertiary-container/10 p-2 rounded-lg">warning</span>
            </div>
            <div className="font-display-lg text-4xl font-bold text-on-surface relative z-10">{stats.total_clusters}</div>
          </div>
          
          {/* Card 3 */}
          <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 group transition-transform duration-300 hover:scale-[1.02] hover:border-secondary-container/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-secondary-container/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex justify-between items-start relative z-10">
              <h3 className="font-headline-sm text-xl font-semibold text-on-surface">System Status</h3>
              <span className="material-symbols-outlined text-secondary-container bg-secondary-container/10 p-2 rounded-lg">monitoring</span>
            </div>
            <div className="font-display-lg text-4xl font-bold text-secondary-container relative z-10">Online</div>
          </div>
        </section>

        {/* Grid for side-by-side layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Chart Section */}
          <section className="glass-panel p-6 rounded-xl relative overflow-hidden flex flex-col">
              <h2 className="text-xl font-headline-sm font-semibold mb-6 flex items-center gap-2">
                Opportunity Score Ranking
              </h2>
              <div className="h-[400px] w-full flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clusters} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                    <XAxis type="number" stroke="#bbcac6" />
                    <YAxis dataKey="cluster_name" type="category" width={150} stroke="#bbcac6" fontSize={12} />
                    <Tooltip 
                      cursor={{fill: 'rgba(255,255,255,0.05)'}}
                      contentStyle={{ backgroundColor: '#1a211f', border: '1px solid #3c4947', borderRadius: '8px' }}
                    />
                    <Bar dataKey="opportunity_score" radius={[0, 4, 4, 0]}>
                      {clusters.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#14b8a6' : '#2f3634'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
          </section>

          {/* Cluster Breakdown Section */}
          <section className="glass-panel p-6 rounded-xl overflow-y-auto max-h-[500px] scrollbar-hide flex flex-col">
            <h2 className="text-xl font-headline-sm font-semibold mb-6">Cluster Breakdown</h2>
            <div className="flex flex-col gap-3">
              {clusters.map((cluster, i) => (
                <div 
                  key={i} 
                  onClick={() => openCluster(cluster)}
                  className="group p-4 rounded-xl bg-black/40 border border-white/5 hover:border-primary-container/50 cursor-pointer transition-all flex items-center justify-between"
                >
                  <div>
                    <h3 className="font-body-md font-semibold text-on-surface group-hover:text-primary transition-colors">
                      {cluster.cluster_name}
                    </h3>
                    <p className="text-xs text-on-surface-variant mt-1">
                      Volume: <span className="text-on-surface font-medium">{cluster.prevalence}</span> &nbsp;&bull;&nbsp; 
                      Score: <span className="text-primary font-medium">{cluster.opportunity_score.toFixed(1)}</span>
                    </p>
                  </div>
                  <ChevronRight className="text-on-surface-variant group-hover:text-primary transition-colors" size={20} />
                </div>
              ))}
            </div>
          </section>
        </div>
        </>
      )}

      {activeTab === "Inventory" && (
        <div className="animate-fade-in-up">
          <header className="mb-12 flex flex-col gap-6">
            <div>
              <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
                Friction-Prone Products Catalog
              </h1>
              <p className="font-body-lg text-lg text-on-surface-variant mt-2">
                Products frequently abandoned in wishlists and their associated friction points.
              </p>
            </div>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {[
              { name: "Levi's 501 Original Fit Jeans", img: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80", score: 92.5, friction: "Missing Size Chart", cluster: "Size & Fit Uncertainty" },
              { name: "Puma RS-X Sneakers", img: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80", score: 89.0, friction: "Constantly OOS", cluster: "Restock Blindness" },
              { name: "GAP Logo Hoodie", img: "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500&q=80", score: 85.5, friction: "Awaiting Price Drop", cluster: "Price Volatility & Coupons" },
              { name: "Biba Embroidered Kurta", img: "https://images.unsplash.com/photo-1603344710174-8dbb242e97a3?w=500&q=80", score: 82.0, friction: "No Customer Review Photos", cluster: "Missing Social Validation" },
              { name: "Nike Air Max 270", img: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80", score: 80.5, friction: "Wishlist Capacity Bug", cluster: "Wishlist Capacity Limits" },
              { name: "H&M Oversized T-Shirt", img: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80", score: 78.0, friction: "Vague Fabric Description", cluster: "Missing Social Validation" }
            ].map((item, idx) => (
              <div key={idx} className="glass-panel rounded-xl overflow-hidden group hover:border-primary-container/50 transition-all flex flex-col">
                <div className="h-48 w-full overflow-hidden relative">
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-all z-10"></div>
                  <img src={item.img} alt={item.name} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-3 right-3 z-20 bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    <span className="text-xs font-bold text-white">Score: {item.score}</span>
                  </div>
                </div>
                <div className="p-5 flex flex-col gap-3">
                  <h3 className="font-headline-sm text-lg font-semibold text-on-surface">{item.name}</h3>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-on-surface-variant">Top Friction Point:</span>
                    <span className="text-sm font-medium text-tertiary-container flex items-center gap-1">
                      <span className="material-symbols-outlined text-sm">warning</span> {item.friction}
                    </span>
                  </div>
                  <div className="flex flex-col gap-1 mt-2">
                    <span className="text-xs text-on-surface-variant">Associated AI Cluster:</span>
                    <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-primary-fixed w-fit">
                      {item.cluster}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "Feedback" && (
        <div className="animate-fade-in-up flex flex-col items-center justify-center h-full min-h-[60vh] text-center">
           <span className="material-symbols-outlined text-6xl text-primary/30 mb-4">forum</span>
           <h2 className="text-2xl font-headline-sm text-on-surface mb-2">Live Feedback Stream</h2>
           <p className="text-on-surface-variant max-w-md">The live feedback pipeline is currently processing data in the background. Raw App Store and Play Store reviews will appear here once the ingestion task completes.</p>
        </div>
      )}

      </main>

      {/* Modal */}
      {selectedCluster && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#121212] border border-white/10 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-headline-sm font-semibold text-primary">{selectedCluster.cluster_name}</h2>
                <p className="text-sm text-on-surface-variant mt-1">Raw Frictions Extracted by AI</p>
              </div>
              <button onClick={() => setSelectedCluster(null)} className="p-2 rounded-full hover:bg-white/10 text-on-surface-variant hover:text-on-surface transition-colors">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-4">
              {insights.length === 0 ? (
                <div className="text-center text-on-surface-variant py-12">Loading raw friction data...</div>
              ) : (
                insights.map((ins, i) => (
                  <div key={i} className="p-5 rounded-xl bg-white/5 border border-white/5">
                    <p className="text-on-surface leading-relaxed text-sm">"{ins.problem_statement}"</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-primary-container/10 text-primary border border-primary-container/20">
                        {ins.topic}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-tertiary-container/10 text-tertiary border border-tertiary-container/20">
                        {ins.intent}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
