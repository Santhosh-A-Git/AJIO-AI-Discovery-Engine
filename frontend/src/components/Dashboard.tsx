"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { X, ChevronRight } from "lucide-react";

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
      <aside className="hidden md:flex flex-col h-screen w-64 fixed left-0 top-0 bg-surface border-r border-white/10 z-40 py-6">
        <div className="px-6 mb-8">
          <h1 className="font-headline-md text-2xl font-semibold text-primary">Discovery Engine</h1>
          <p className="font-body-sm text-sm text-on-surface-variant mt-1">Premium Curator v2.1</p>
        </div>
        <nav className="flex-1 px-2 space-y-2">
          <a className="bg-white/10 text-primary border-r-4 border-primary px-4 py-3 flex items-center gap-3 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold" href="#">
            <span className="material-symbols-outlined">dashboard</span>
            Dashboard
          </a>
          <a className="text-on-surface-variant px-4 py-3 flex items-center gap-3 hover:backdrop-blur-xl hover:bg-white/10 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold" href="#">
            <span className="material-symbols-outlined">trending_up</span>
            Trends
          </a>
          <a className="text-on-surface-variant px-4 py-3 flex items-center gap-3 hover:backdrop-blur-xl hover:bg-white/10 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold" href="#">
            <span className="material-symbols-outlined">inventory_2</span>
            Inventory
          </a>
          <a className="text-on-surface-variant px-4 py-3 flex items-center gap-3 hover:backdrop-blur-xl hover:bg-white/10 transition-all duration-200 ease-in-out font-label-bold text-xs uppercase font-bold" href="#">
            <span className="material-symbols-outlined">comment</span>
            Feedback
          </a>
        </nav>
        <div className="px-4 mt-auto">
          <button className="w-full bg-primary-container text-on-primary-container py-3 rounded font-label-bold text-xs uppercase font-bold hover:bg-primary-fixed transition-colors">
            Generate Report
          </button>
        </div>
        <div className="px-6 mt-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full border border-white/10 bg-primary/20 flex items-center justify-center text-primary font-bold">A</div>
          <div className="font-body-sm text-sm text-on-surface">AJIO Admin</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 p-6 md:p-10 w-full max-w-container-max-width mx-auto">
        
        {/* Header & Semantic Search */}
        <header className="mb-12 flex flex-col gap-6">
          <div>
            <h1 className="font-display-lg text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-container to-secondary-container bg-clip-text text-transparent w-fit">
              AJIO Product Discovery Engine
            </h1>
            <p className="font-body-lg text-lg text-on-surface-variant mt-2">
              AI-powered friction analysis from multi-channel user feedback.
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
              className="absolute inset-y-2 right-2 px-6 bg-primary-container text-on-primary-container rounded-lg font-label-bold text-sm hover:bg-primary-fixed transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSearching ? <span className="material-symbols-outlined animate-spin text-sm">sync</span> : 'Ask AI'}
            </button>
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
                        return <div key={j} className="text-primary-container font-bold text-base mt-4 mb-1">{part.slice(2, -2).trim()}</div>;
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

        {/* Chart & List Section */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Chart Section */}
          <div className="col-span-1 lg:col-span-2 glass-panel p-6 rounded-xl relative overflow-hidden">
            <h2 className="text-xl font-headline-sm font-semibold mb-6 flex items-center gap-2">
              Opportunity Score Ranking
            </h2>
            <div className="h-[400px] w-full">
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
          </div>

          {/* List Section */}
          <div className="col-span-1 glass-panel p-6 rounded-xl overflow-y-auto max-h-[500px] scrollbar-hide">
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
          </div>

        </section>

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
