import { useEffect, useState } from "react";
import { api } from "../api/client";
type O = { id: number; ticket_code: string; garment_name: string; due_at: string; status: string; length_cm?: number };
type Seg = { ticket_code: string; start_cm: number; end_cm: number };
function holdNote(rows: O[], segs: Seg[]) {
  const tickets = new Set(segs.map(s => s.ticket_code));
  const still = rows.filter(o => o.status === "overdue" && tickets.has(o.ticket_code));
  const ghost = segs.filter(s => !rows.some(o => o.ticket_code === s.ticket_code && o.status === "hung"));
  if (!still.length && !ghost.length) return "";
  return `仍占杆 ${still.length} 单，图上段 ${segs.length}，其中非在挂段 ${ghost.length}`;
}

export default function OverduePage() {
  const [rows, setRows] = useState<O[]>([]);
  const [segs, setSegs] = useState<Seg[]>([]);
  const [msg, setMsg] = useState("");
  const reload = () => {
    api<O[]>("/overdue").then(setRows);
    api<{ segments: Seg[] }>("/occupancy/1").then(m => setSegs(m.segments || [])).catch(() => setSegs([]));
  };
  useEffect(() => { reload(); }, []);
  async function scan() {
    const marked = await api<O[]>("/overdue/scan", { method: "POST", body: "{}" });
    setMsg(`扫描完成，新标记 ${marked.length} 单`);
    reload();
  }
  return (<>
    <h2>逾期</h2>
    <div className="toolbar"><button onClick={scan}>扫描逾期</button>{msg && <span className="ok">{msg}</span>}{holdNote(rows, segs) && <span className="muted-tip">{holdNote(rows, segs)}</span>}</div>
    <table className="table"><thead><tr><th>票号</th><th>衣物</th><th>到期</th><th>状态</th></tr></thead>
    <tbody>{rows.map(o => <tr key={o.id}><td className="mono">{o.ticket_code}</td><td>{o.garment_name}</td><td className="mono">{new Date(o.due_at).toLocaleString()}</td><td>{o.status}</td></tr>)}
      {!rows.length && <tr><td colSpan={4}>暂无逾期</td></tr>}
    </tbody></table>
  </>);
}
