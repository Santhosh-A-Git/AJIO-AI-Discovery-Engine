"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { X, ChevronRight, Download } from "lucide-react";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export default function Dashboard() {
  const [stats, setStats] = useState<any>({});
  const [clusters, setClusters] = useState<any[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<any>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [sourcesList, setSourcesList] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("Discover");

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
        const [statsRes, clustersRes, feedbacksRes, sourcesRes] = await Promise.all([
          axios.get(`${API_BASE}/stats`),
          axios.get(`${API_BASE}/clusters`),
          axios.get(`${API_BASE}/feedback`),
          axios.get(`${API_BASE}/sources`)
        ]);
        setStats(statsRes.data);
        setClusters(clustersRes.data);
        setFeedbacks(feedbacksRes.data);
        setSourcesList(sourcesRes.data);
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
    doc.text("Discovery Funnel:", 14, 50);
    doc.setFontSize(11);
    doc.text(`Raw Records Collected: ${stats.raw_records_collected || 0}`, 14, 58);
    doc.text(`Unique Observations: ${stats.unique_records || 0}`, 14, 64);
    doc.text(`Relevant Observations: ${stats.relevant_observations || 0}`, 14, 70);
    doc.text(`Opportunity Clusters: ${stats.opportunity_clusters || 0}`, 14, 76);
    
    let yPos = 88;
    
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
      
      if (searchResult.structured_insights) {
        searchResult.structured_insights.forEach((insight: any) => {
          const insightText = `**${insight.headline}:** ${insight.explanation}`;
          const splitInsight = doc.splitTextToSize(insightText, 180);
          doc.text(splitInsight, 14, yPos);
          yPos += (splitInsight.length * 6) + 4;
          
          if (insight.evidence) {
            const evText = `[Evidence Breakdown]
Theme: ${insight.evidence.theme} | Strength: ${insight.evidence.evidence_strength}
Source: ${insight.evidence.source}
Clue: ${insight.evidence.user_segment_clue}
Intent: ${insight.evidence.wishlist_intent}
Why Saved: ${insight.evidence.why_saved}
Blocker: ${insight.evidence.conversion_blocker}
Uncertainty: ${insight.evidence.uncertainty}
Workaround: ${insight.evidence.workaround}
External: ${insight.evidence.external_platform_used}
Status: ${insight.evidence.purchase_status}`;
            const splitEv = doc.splitTextToSize(evText, 170);
            doc.text(splitEv, 18, yPos);
            yPos += (splitEv.length * 5) + 6;
          }
        });
      } else if (searchResult.answer) {
        const splitAnswer = doc.splitTextToSize(searchResult.answer, 180);
        doc.text(splitAnswer, 14, yPos);
        yPos += (splitAnswer.length * 6) + 10;
      }
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
      c.cluster_name + (c.research_hypothesis ? `\n\nAI Hypothesis:\n${c.research_hypothesis}` : ''),
      c.prevalence.toString(),
      (c.opportunity_score || 0).toFixed(1)
    ]);
    
    autoTable(doc, {
      startY: yPos + 6,
      head: [['Cluster Name & Hypothesis', 'Vol', 'Score']],
      body: tableData,
      theme: 'grid',
      headStyles: { fillColor: [20, 184, 166] },
      styles: { cellWidth: 'wrap' },
      columnStyles: { 0: { cellWidth: 130 } }
    });
    
    // Supporting Evidence Section
    const finalY = (doc as any).lastAutoTable.finalY || yPos + 20;
    let evY = finalY + 15;
    
    if (searchQuery && searchResult && searchResult.sources && searchResult.sources.length > 0) {
      if (evY > 250) {
        doc.addPage();
        evY = 20;
      }
      doc.setFontSize(14);
      doc.setTextColor(20, 184, 166);
      doc.text("Supporting Evidence (AI Processed Relevant Data):", 14, evY);
      evY += 8;
      
      searchResult.sources.forEach((src: any, idx: number) => {
        if (evY > 270) {
          doc.addPage();
          evY = 20;
        }
        doc.setFontSize(10);
        doc.setTextColor(0);
        const sourceText = `[${idx+1}] Source: ${src.source} | Strength: ${src.evidence_strength} | Segment: ${src.user_segment_clue}`;
        doc.text(sourceText, 14, evY);
        evY += 5;
        
        doc.setFontSize(9);
        doc.setTextColor(80);
        // Clean up text
        let cleanText = src.original_text || src.problem_statement;
        if (cleanText) {
            const splitEvText = doc.splitTextToSize(`"${cleanText}"`, 180);
            doc.text(splitEvText, 14, evY);
            evY += (splitEvText.length * 4) + 6;
        }
      });
    }
    
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
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Discover"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Discover" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">explore</span>
            Discover
          </a>
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Opportunity Landscape"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Opportunity Landscape" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">insights</span>
            Opportunity Landscape
          </a>
          <a onClick={(e) => { e.preventDefault(); setActiveTab("Evidence Explorer"); }} className={`cursor-pointer px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold ${activeTab === "Evidence Explorer" ? "bg-white/10 text-primary border-r-4 border-primary" : "text-on-surface-variant hover:backdrop-blur-xl hover:bg-white/10"}`} href="#">
            <span className="material-symbols-outlined">manage_search</span>
            Evidence Explorer
          </a>
          <div className="pt-4 px-2">
            <button onClick={generatePDFReport} className="w-full bg-primary-container text-on-primary-container py-3 rounded-lg font-label-bold text-sm hover:bg-primary-fixed transition-colors flex items-center justify-center gap-2 shadow-sm">
              <span className="material-symbols-outlined text-sm">download</span>
              GENERATE REPORT
            </button>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-80 p-6 md:p-10 w-full max-w-container-max-width mx-auto">
        
        {activeTab === "Discover" && (
          <>
            {/* Header & Semantic Search */}
            <header className="mb-12 flex flex-col gap-6">
          <div>
            <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
              Discover The Unmet
            </h1>
            <p className="font-body-lg text-lg text-on-surface-variant mt-2">
              AI-Powered Friction Analysis From Multi-Channel User Feedback
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
              placeholder="What prevents wishlisted products from eventually being purchased?"
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
                "What information do users seek outside AJIO before purchasing?",
                "What role do fit, size, styling, price, reviews, occasion and social validation play?",
                "When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?",
                "How do user behaviors differ across user segments?",
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
              <div className="text-on-surface text-sm leading-relaxed mb-6">
                {searchResult.structured_insights ? (
                  <div className="flex flex-col gap-6">
                    {searchResult.structured_insights.map((insight: any, i: number) => (
                      <div key={i} className="flex flex-col gap-3">
                        <p className="whitespace-pre-wrap">
                          <span className="text-primary font-extrabold text-[15px] tracking-wide mr-2">{insight.headline}:</span>
                          <span>{insight.explanation}</span>
                        </p>
                        
                        {insight.evidence && (
                          <div className="bg-black/30 rounded-lg p-4 border border-white/5 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs mt-2 animate-fade-in-up">
                            <div className="col-span-1 md:col-span-2 border-b border-white/5 pb-2 mb-1 flex items-center justify-between">
                              <span className="font-label-bold text-on-surface-variant uppercase tracking-wider">Evidence Breakdown</span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${insight.evidence.evidence_strength === 'High' ? 'bg-error/20 text-error' : 'bg-primary/20 text-primary'}`}>{insight.evidence.evidence_strength} Evidence</span>
                            </div>
                            
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Source</span>
                              <span className="font-medium">{insight.evidence.source}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Theme</span>
                              <span className="font-medium">{insight.evidence.theme}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">User Segment Clue</span>
                              <span className="font-medium">{insight.evidence.user_segment_clue}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Wishlist Intent</span>
                              <span className="font-medium">{insight.evidence.wishlist_intent}</span>
                            </div>
                            <div className="flex flex-col gap-1 col-span-1 md:col-span-2">
                              <span className="text-on-surface-variant opacity-60">Why Saved</span>
                              <span className="font-medium">{insight.evidence.why_saved}</span>
                            </div>
                            <div className="flex flex-col gap-1 col-span-1 md:col-span-2 text-error">
                              <span className="text-error opacity-80">Conversion Blocker</span>
                              <span className="font-bold">{insight.evidence.conversion_blocker}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Uncertainty</span>
                              <span className="font-medium">{insight.evidence.uncertainty}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Workaround</span>
                              <span className="font-medium">{insight.evidence.workaround}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">External Platform</span>
                              <span className="font-medium">{insight.evidence.external_platform_used}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-on-surface-variant opacity-60">Purchase Status</span>
                              <span className="font-medium">{insight.evidence.purchase_status}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap">
                    {searchResult.answer?.split('\n').map((line: string, i: number) => (
                      <React.Fragment key={i}>
                        {line.split(/(\*\*.*?\*\*)/).map((part: string, j: number) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            const cleanTitle = part.replace(/\*\*/g, '').trim().replace(/:$/, '');
                            return (
                              <span key={j} className="text-primary font-extrabold text-[15px] tracking-wide mr-2">
                                {cleanTitle}:
                              </span>
                            );
                          }
                          return <span key={j}>{part}</span>;
                        })}
                        {i < searchResult.answer.split('\n').length - 1 && <br />}
                      </React.Fragment>
                    ))}
                  </div>
                )}
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
        
        {activeTab === "Opportunity Landscape" && (
          <>
            <header className="mb-12 flex flex-col gap-6">
              <div>
                <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
                  AI Opportunity Matrix
                </h1>
                <p className="font-body-lg text-lg text-on-surface-variant mt-2">
                  Algorithmic prioritization of user friction to maximize conversion velocity.
                </p>
              </div>
            </header>

            {/* Discovery Funnel KPI Banner */}
            <section className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-12">
          {/* Raw Records */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2">
            <h3 className="font-headline-sm text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Raw Records</h3>
            <div className="font-display-lg text-2xl font-bold text-on-surface">{stats.raw_records_collected || 0}</div>
          </div>
          
          {/* Unique Records */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2">
            <h3 className="font-headline-sm text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Unique</h3>
            <div className="font-display-lg text-2xl font-bold text-on-surface">{stats.unique_records || 0}</div>
          </div>
          
          {/* AI Analyzed */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2">
            <h3 className="font-headline-sm text-xs font-semibold text-on-surface-variant uppercase tracking-wider">AI Analyzed</h3>
            <div className="font-display-lg text-2xl font-bold text-on-surface">{stats.ai_analyzed_records || 0}</div>
          </div>

          {/* Relevant */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2 border border-primary/20 bg-primary/5">
            <h3 className="font-headline-sm text-xs font-semibold text-primary uppercase tracking-wider">Relevant</h3>
            <div className="font-display-lg text-2xl font-bold text-primary">{stats.relevant_observations || 0}</div>
          </div>

          {/* Possibly Relevant */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2">
            <h3 className="font-headline-sm text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Possibly Relevant</h3>
            <div className="font-display-lg text-2xl font-bold text-on-surface">{stats.possibly_relevant_observations || 0}</div>
          </div>

          {/* Clusters */}
          <div className="glass-panel p-4 rounded-xl flex flex-col gap-2 border border-tertiary-container/20 bg-tertiary-container/5">
            <h3 className="font-headline-sm text-xs font-semibold text-tertiary-container uppercase tracking-wider">Clusters</h3>
            <div className="font-display-lg text-2xl font-bold text-tertiary-container">{stats.opportunity_clusters || 0}</div>
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
                  <div className="w-full">
                    <div className="flex justify-between items-center w-full">
                      <h3 className="font-body-md font-semibold text-on-surface group-hover:text-primary transition-colors flex items-center gap-2">
                        {cluster.cluster_name}
                        {cluster.prevalence < 3 && (
                           <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-error/20 text-error border border-error/30 uppercase tracking-widest whitespace-nowrap">Directional / Low Evidence</span>
                        )}
                      </h3>
                      <ChevronRight className="text-on-surface-variant group-hover:text-primary transition-colors" size={20} />
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-2 text-xs text-on-surface-variant">
                      <span>Vol: <b className="text-on-surface">{cluster.prevalence}</b></span>
                      <span>Rel: <b className="text-on-surface">{cluster.intent_relevance_norm?.toFixed(0)}</b></span>
                      <span>Str: <b className="text-on-surface">{cluster.evidence_strength_norm?.toFixed(0)}</b></span>
                      <span>Sev: <b className="text-on-surface">{cluster.severity_norm?.toFixed(0)}</b></span>
                      <span>Src: <b className="text-on-surface">{cluster.cross_source_norm?.toFixed(0)}</b></span>
                      <span>Seg: <b className="text-on-surface">{cluster.segment_concentration_norm?.toFixed(0)}</b></span>
                      <span className="ml-auto">Score: <b className="text-primary text-sm">{(cluster.opportunity_score || 0).toFixed(1)}</b></span>
                    </div>
                    {cluster.research_hypothesis && (
                      <div className="mt-4 p-3 rounded bg-primary/5 border border-primary/10 text-on-surface-variant text-sm leading-relaxed">
                        <span className="font-bold text-primary block mb-1 uppercase tracking-widest text-[10px] flex items-center gap-1">
                          <span className="material-symbols-outlined text-[12px]">science</span>
                          AI Research Hypothesis
                        </span>
                        <span className="italic text-on-surface">"{cluster.research_hypothesis}"</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
        </>
      )}



      {activeTab === "Evidence Explorer" && (
        <div className="animate-fade-in-up">
           <div className="flex justify-between items-center mb-6">
             <h2 className="font-headline-md text-2xl font-bold text-on-surface">User Feedback Evidence</h2>
             <div className="flex gap-2">
               <select 
                 className="bg-surface-variant text-xs text-fuchsia-500 font-bold uppercase p-2 rounded border border-white/10"
                 onChange={(e) => {
                   const val = e.target.value;
                   axios.get(`${API_BASE}/feedback?relevance=${val}`).then(res => setFeedbacks(res.data));
                 }}
               >
                 <option value="">ALL RELEVANCE</option>
                 <option value="RELEVANT">RELEVANT ONLY</option>
                 <option value="POSSIBLY_RELEVANT">POSSIBLY_RELEVANT</option>
                 <option value="NOT_RELEVANT">NOT_RELEVANT</option>
               </select>
               <select 
                 className="bg-surface-variant text-xs text-fuchsia-500 font-bold uppercase p-2 rounded border border-white/10"
                 onChange={(e) => {
                   const val = e.target.value;
                   axios.get(`${API_BASE}/feedback?source_type=${val}`).then(res => setFeedbacks(res.data));
                 }}
               >
                 <option value="">ALL SOURCES</option>
                 {sourcesList.map(src => (
                   <option key={src} value={src}>{src}</option>
                 ))}
               </select>
             </div>
           </div>
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
             {[...feedbacks].sort((a, b) => {
               const getIndex = (src: string) => {
                 if (!src) return 999;
                 const s = src.toLowerCase();
                 if (s.includes('play')) return 0;
                 if (s.includes('app')) return 1;
                 if (s.includes('youtube')) return 2;
                 if (s.includes('twitter')) return 3;
                 if (s.includes('web') || s.includes('search')) return 4;
                 if (s.includes('news')) return 5;
                 return 999;
               };
               return getIndex(a.source) - getIndex(b.source);
             }).map((f, i) => (
               <div key={i} className="glass-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors flex flex-col justify-between">
                 <div>
                   <div className="flex justify-between items-start mb-3">
                     <span className="text-[10px] font-bold text-primary-container px-2 py-1 bg-primary/10 rounded border border-primary/20 uppercase tracking-widest">{f.source || 'USER_GENERATED'}</span>
                     <span className="text-xs text-on-surface-variant opacity-60">{f.date || f.timestamp ? new Date(f.date || f.timestamp).toLocaleDateString() : 'Recent'}</span>
                   </div>
                   <p className="text-sm text-on-surface-variant leading-relaxed line-clamp-6">{f.text}</p>
                 </div>
                 <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center">
                   <span className="text-[10px] font-mono text-tertiary-container">{f.id ? `ID: ${f.id.substring(0,8)}...` : 'ID: UNKNOWN'}</span>
                   {f.url && <a href={f.url} target="_blank" rel="noreferrer" className="text-[10px] text-primary underline">Source Link</a>}
                 </div>
               </div>
             ))}
           </div>
           {feedbacks.length === 0 && (
             <div className="text-center py-20 text-on-surface-variant">
               No raw evidence found. Ensure the ingestion pipeline has completed.
             </div>
           )}
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
                    <div className="flex justify-between items-start mb-2">
                       <span className="text-[10px] font-bold text-primary px-2 py-0.5 bg-primary/10 rounded border border-primary/20 uppercase tracking-widest">{ins.source}</span>
                       <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest ${ins.evidence_strength === 'HIGH' ? 'bg-error/20 text-error border-error/30' : 'bg-tertiary/20 text-tertiary border-tertiary/30'}`}>{ins.evidence_strength} Evidence</span>
                    </div>
                    <p className="text-on-surface leading-relaxed text-sm mb-3">"{ins.original_text}"</p>
                    
                    <div className="bg-black/30 p-3 rounded mt-2 border border-white/5">
                      <p className="text-xs text-on-surface-variant mb-1"><span className="text-primary opacity-80 font-semibold mr-1">Observed Friction:</span> {ins.observed_problem_summary}</p>
                      <p className="text-xs text-on-surface-variant mb-1"><span className="text-primary opacity-80 font-semibold mr-1">Relevance:</span> {ins.relevance_status}</p>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="px-3 py-1 rounded-full text-[10px] font-medium bg-primary-container/10 text-primary border border-primary-container/20">
                        Intent: {ins.wishlist_intent}
                      </span>
                      <span className="px-3 py-1 rounded-full text-[10px] font-medium bg-error/10 text-error border border-error/20">
                        Blocker: {ins.conversion_blocker}
                      </span>
                      <span className="px-3 py-1 rounded-full text-[10px] font-medium bg-tertiary-container/10 text-tertiary border border-tertiary-container/20">
                        Status: {ins.purchase_status}
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
