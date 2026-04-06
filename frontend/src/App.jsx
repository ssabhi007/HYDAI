import { useState, useEffect } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const API = "http://127.0.0.1:8000"

const COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#ec4899"]

export default function App() {
  const [areas, setAreas]       = useState([])
  const [issues, setIssues]     = useState([])
  const [urgent, setUrgent]     = useState([])
  const [hotspots, setHotspots] = useState([])
  const [briefing, setBriefing] = useState("")
  const [chat, setChat]         = useState([])
  const [input, setInput]       = useState("")
  const [tab, setTab]           = useState("dashboard")

  useEffect(() => {
    axios.get(`${API}/stats/areas`).then(r => setAreas(r.data))
    axios.get(`${API}/stats/issues`).then(r => setIssues(r.data))
    axios.get(`${API}/stats/urgent`).then(r => setUrgent(r.data))
    axios.get(`${API}/stats/hotspots`).then(r => setHotspots(r.data))
    axios.get(`${API}/briefing`).then(r => setBriefing(r.data.briefing))
  }, [])

  const sendMessage = async () => {
    if (!input.trim()) return
    const userMsg = { role: "user", text: input }
    setChat(prev => [...prev, userMsg])
    setInput("")

    const context = `
      You are HYDAI, urban issue assistant for Hyderabad.
      Top areas: ${areas.map(a => `${a.area}(${a.count})`).join(", ")}
      Issues: ${issues.map(i => `${i.issue}(${i.count})`).join(", ")}
      Urgent: ${urgent.slice(0,3).map(u => `${u.location} ${u.issue_category} ${u.duration_days}days`).join(", ")}
      Answer based only on this data. Be concise.
      Question: ${input}
    `
    const res = await axios.post(`${API}/chat`, { message: context })
    setChat(prev => [...prev, { role: "hydai", text: res.data.reply }])
  }

  return (
    <div style={{ fontFamily: "sans-serif", background: "#0f172a", minHeight: "100vh", color: "#e2e8f0" }}>

      {/* Header */}
      <div style={{ background: "#1e293b", padding: "16px 32px", display: "flex", alignItems: "center", gap: 16, borderBottom: "1px solid #334155" }}>
        <div style={{ background: "#6366f1", borderRadius: 8, padding: "6px 12px", fontWeight: 700, fontSize: 18 }}>HYDAI</div>
        <span style={{ color: "#94a3b8", fontSize: 14 }}>Hyderabad Urban Issue Intelligence</span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {["dashboard","briefing","chat"].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ padding: "6px 16px", borderRadius: 6, border: "none", cursor: "pointer",
                background: tab === t ? "#6366f1" : "#334155",
                color: tab === t ? "#fff" : "#94a3b8", fontWeight: 600, textTransform: "capitalize" }}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div style={{ padding: 32 }}>

        {/* DASHBOARD TAB */}
        {tab === "dashboard" && (
          <div>
            {/* Stat Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 32 }}>
              {[
                { label: "Total Areas",    value: areas.length,                       color: "#6366f1" },
                { label: "Issue Types",    value: issues.length,                      color: "#f59e0b" },
                { label: "Urgent Cases",   value: urgent.length,                      color: "#ef4444" },
                { label: "Hotspots",       value: hotspots.length,                    color: "#10b981" },
              ].map(card => (
                <div key={card.label} style={{ background: "#1e293b", borderRadius: 12, padding: 20, borderLeft: `4px solid ${card.color}` }}>
                  <div style={{ fontSize: 32, fontWeight: 700, color: card.color }}>{card.value}</div>
                  <div style={{ color: "#94a3b8", fontSize: 14 }}>{card.label}</div>
                </div>
              ))}
            </div>

            {/* Charts Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>

              {/* Bar Chart - Areas */}
              <div style={{ background: "#1e293b", borderRadius: 12, padding: 24 }}>
                <div style={{ fontWeight: 600, marginBottom: 16, color: "#e2e8f0" }}>Complaints by Area</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={areas}>
                    <XAxis dataKey="area" tick={{ fill: "#94a3b8", fontSize: 11 }} angle={-30} textAnchor="end" height={60}/>
                    <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }}/>
                    <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }}/>
                    <Bar dataKey="count" fill="#6366f1" radius={[4,4,0,0]}/>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Pie Chart - Issues */}
              <div style={{ background: "#1e293b", borderRadius: 12, padding: 24 }}>
                <div style={{ fontWeight: 600, marginBottom: 16, color: "#e2e8f0" }}>Issue Distribution</div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={issues} dataKey="count" nameKey="issue" cx="50%" cy="50%" outerRadius={90} label={({issue,percent}) => `${issue} ${(percent*100).toFixed(0)}%`}>
                      {issues.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]}/>)}
                    </Pie>
                    <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }}/>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Urgent Table */}
            <div style={{ background: "#1e293b", borderRadius: 12, padding: 24 }}>
              <div style={{ fontWeight: 600, marginBottom: 16, color: "#ef4444" }}>🚨 Urgent Cases</div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid #334155" }}>
                    {["Area","Issue","Days","Summary"].map(h => (
                      <th key={h} style={{ textAlign: "left", padding: "8px 12px", color: "#94a3b8", fontSize: 13 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {urgent.map((u, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                      <td style={{ padding: "10px 12px", color: "#f59e0b", fontWeight: 600 }}>{u.location}</td>
                      <td style={{ padding: "10px 12px" }}>
                        <span style={{ background: "#312e81", color: "#a5b4fc", padding: "2px 8px", borderRadius: 4, fontSize: 12 }}>{u.issue_category}</span>
                      </td>
                      <td style={{ padding: "10px 12px", color: "#ef4444", fontWeight: 700 }}>{u.duration_days}d</td>
                      <td style={{ padding: "10px 12px", color: "#94a3b8", fontSize: 13 }}>{u.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* BRIEFING TAB */}
        {tab === "briefing" && (
          <div style={{ background: "#1e293b", borderRadius: 12, padding: 32, whiteSpace: "pre-wrap", lineHeight: 1.8, color: "#e2e8f0" }}>
            <div style={{ fontWeight: 700, fontSize: 20, marginBottom: 24, color: "#6366f1" }}>HYDAI Daily Briefing Report</div>
            {briefing || "Loading briefing..."}
          </div>
        )}

        {/* CHAT TAB */}
        {tab === "chat" && (
          <div style={{ background: "#1e293b", borderRadius: 12, padding: 24, height: "70vh", display: "flex", flexDirection: "column" }}>
            <div style={{ fontWeight: 600, marginBottom: 16, color: "#6366f1" }}>Chat with HYDAI</div>
            <div style={{ flex: 1, overflowY: "auto", marginBottom: 16, display: "flex", flexDirection: "column", gap: 12 }}>
              {chat.length === 0 && (
                <div style={{ color: "#475569", textAlign: "center", marginTop: 40 }}>
                  Ask me anything about Hyderabad urban issues...
                </div>
              )}
              {chat.map((m, i) => (
                <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                  <div style={{
                    maxWidth: "70%", padding: "10px 16px", borderRadius: 12,
                    background: m.role === "user" ? "#6366f1" : "#334155",
                    color: "#e2e8f0", fontSize: 14, lineHeight: 1.6
                  }}>{m.text}</div>
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <input value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && sendMessage()}
                placeholder="Ask about Hyderabad complaints..."
                style={{ flex: 1, padding: "10px 16px", borderRadius: 8, border: "1px solid #334155",
                  background: "#0f172a", color: "#e2e8f0", fontSize: 14, outline: "none" }}/>
              <button onClick={sendMessage}
                style={{ padding: "10px 24px", borderRadius: 8, border: "none",
                  background: "#6366f1", color: "#fff", fontWeight: 600, cursor: "pointer" }}>
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}