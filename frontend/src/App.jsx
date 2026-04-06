import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"

import { useState, useEffect } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const API = "http://127.0.0.1:8000"

const COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#ec4899"]

const AREA_COORDS = {
  "kondapur"       : [17.4598, 78.3677],
  "kukatpally"     : [17.4849, 78.3953],
  "hitech city"    : [17.4435, 78.3772],
  "madhapur"       : [17.4486, 78.3908],
  "jubilee hills"  : [17.4317, 78.4071],
  "mehdipatnam"    : [17.3953, 78.4380],
  "lb nagar"       : [17.3470, 78.5529],
  "uppal"          : [17.4051, 78.5587],
  "tolichowki"     : [17.4076, 78.4183],
  "nagole"         : [17.3861, 78.5604],
  "dilsukhnagar"   : [17.3687, 78.5247],
  "sainikpuri"     : [17.4849, 78.5524],
  "attapur"        : [17.3726, 78.4221],
  "hayathnagar"    : [17.3271, 78.6069],
  "vanasthalipuram": [17.3372, 78.5476],
  "amberpet"       : [17.4130, 78.5172],
  "bachupally"     : [17.5432, 78.4102],
  "chandanagar"    : [17.4924, 78.3295],
  "alwal"          : [17.5041, 78.5022],
  "kompally"       : [17.5408, 78.4862],
  "medchal"        : [17.6277, 78.4800],
  "gachibowli"     : [17.4401, 78.3489],
  "banjara hills"  : [17.4138, 78.4382],
  "secunderabad"   : [17.4399, 78.4983],
  "himayatnagar"   : [17.4062, 78.4752],
  "ameerpet"       : [17.4374, 78.4482],
  "old city"       : [17.3578, 78.4740],
  "shamshabad"     : [17.2543, 78.4291],
  "ecil"           : [17.4695, 78.5667],
  "malkajgiri"     : [17.4593, 78.5330],
  "trimulgherry"   : [17.4469, 78.5108],
  "miyapur"        : [17.4959, 78.3468],
  "begumpet"       : [17.4418, 78.4636],
  "kothapet"       : [17.3695, 78.5476],
  "malakpet"       : [17.3780, 78.5020],
  "nampally"       : [17.3833, 78.4739],
  "abids"          : [17.3926, 78.4740],
  "charminar"      : [17.3616, 78.4747],
  "tarnaka"        : [17.4380, 78.5509],
  "moosapet"       : [17.4594, 78.4213],
  "manikonda"      : [17.4025, 78.3893],
  "nallagandla"    : [17.4826, 78.3317],
  "tellapur"       : [17.4936, 78.2994],
  "patancheru"     : [17.5351, 78.2635],
  "ghatkesar"      : [17.4442, 78.6948],
}

const ISSUE_COLORS = {
  "garbage"     : "#f59e0b",
  "traffic"     : "#ef4444",
  "waterlogging": "#3b82f6",
  "pothole"     : "#f97316",
  "streetlight" : "#8b5cf6",
  "water_supply": "#06b6d4",
  "other"       : "#6b7280",
}

export default function App() {
  const [areas, setAreas]       = useState([])
  const [issues, setIssues]     = useState([])
  const [urgent, setUrgent]     = useState([])
  const [hotspots, setHotspots] = useState([])
  const [briefing, setBriefing] = useState("")
  const [chat, setChat]         = useState([])
  const [input, setInput]       = useState("")
  const [tab, setTab]           = useState("dashboard")
  const [complaints, setComplaints] = useState([])

  useEffect(() => {
    axios.get(`${API}/stats/areas`).then(r => setAreas(r.data))
    axios.get(`${API}/stats/issues`).then(r => setIssues(r.data))
    axios.get(`${API}/stats/urgent`).then(r => setUrgent(r.data))
    axios.get(`${API}/stats/hotspots`).then(r => setHotspots(r.data))
    axios.get(`${API}/briefing`).then(r => setBriefing(r.data.briefing))
    axios.get(`${API}/complaints`).then(r => setComplaints(r.data))

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
          {["dashboard","map","briefing","chat"].map(t => (
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

        {/* MAP TAB */}
{tab === "map" && (
  <div style={{ borderRadius: 12, overflow: "hidden", height: "75vh" }}>
    <MapContainer
      center={[17.4065, 78.4772]}
      zoom={12}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="© OpenStreetMap"
      />
      {complaints.map((c, i) => {
        const coords = AREA_COORDS[c.location?.toLowerCase()]
        if (!coords) return null
        const color = ISSUE_COLORS[c.issue_category] || "#6b7280"
        const radius = c.severity === "high" ? 10 : c.severity === "medium" ? 7 : 5
        return (
          <CircleMarker
            key={i}
            center={coords}
            radius={radius}
            fillColor={color}
            color={color}
            fillOpacity={0.7}
            weight={1}
          >
            <Popup>
              <div style={{ minWidth: 180 }}>
                <strong style={{ color: "#1e293b" }}>{c.location}</strong><br/>
                <span style={{ background: color, color: "#fff", padding: "2px 6px", borderRadius: 4, fontSize: 11 }}>
                  {c.issue_category}
                </span><br/><br/>
                <span style={{ fontSize: 12 }}>{c.summary}</span><br/>
                <span style={{ fontSize: 11, color: "#666" }}>
                  Severity: {c.severity} | Days: {c.duration_days}
                </span>
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </MapContainer>

    {/* Legend */}
    <div style={{ position: "absolute", bottom: 40, right: 40, background: "#1e293b",
      padding: 16, borderRadius: 10, zIndex: 1000, border: "1px solid #334155" }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: "#e2e8f0", fontSize: 13 }}>Issue Types</div>
      {Object.entries(ISSUE_COLORS).map(([issue, color]) => (
        <div key={issue} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: color }}/>
          <span style={{ color: "#94a3b8", fontSize: 12, textTransform: "capitalize" }}>{issue}</span>
        </div>
      ))}
    </div>
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