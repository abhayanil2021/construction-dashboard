import React, { useState, useMemo } from "react";
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --navy:#0A1628;--navy2:#112040;--navy3:#1A3260;
  --blue:#1757C2;--bluem:#1E6AE1;--bluelt:#EEF4FF;--blueln:#C5D9F8;
  --t1:#0A1628;--t2:#3A4B6B;--t3:#6E7FA0;
  --surf:#fff;--bg:#F2F5FA;--bdr:#E0E8F4;
  --grn:#1A7A4A;--grnlt:#E6F6EE;--amb:#B45309;--amblt:#FEF3E2;
  --rmd:6px;--rmm:10px;--rml:14px;
}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg);color:var(--t1);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased;}
.shell{display:flex;flex-direction:column;min-height:100vh;}
.topbar{height:60px;background:var(--navy);display:flex;align-items:center;justify-content:space-between;padding:0 40px;position:sticky;top:0;z-index:200;border-bottom:1px solid rgba(255,255,255,0.06);}
.tb-left{display:flex;align-items:center;gap:18px;}
.logomark{width:32px;height:32px;background:var(--bluem);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.logomark svg{width:18px;height:18px;fill:#fff;}
.logo-div{width:1px;height:24px;background:rgba(255,255,255,0.12);}
.logo-name{font-size:13px;font-weight:600;color:#fff;letter-spacing:0.2px;display:block;}
.logo-sub{font-size:10px;font-weight:400;color:rgba(255,255,255,0.36);letter-spacing:0.6px;text-transform:uppercase;display:block;}
.tb-right{display:flex;align-items:center;gap:12px;}
.live-dot{width:7px;height:7px;border-radius:50%;background:#34D399;}
.live-lbl{font-size:11px;color:rgba(255,255,255,0.4);}
.user-chip{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:5px 12px 5px 8px;}
.user-av{width:22px;height:22px;border-radius:50%;background:var(--bluem);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#fff;}
.user-nm{font-size:12px;color:rgba(255,255,255,0.7);font-weight:500;}
.ph{background:var(--navy2);padding:22px 40px;border-bottom:1px solid rgba(255,255,255,0.06);}
.bc{display:flex;align-items:center;gap:8px;margin-bottom:10px;}
.bc-i{font-size:11px;color:rgba(255,255,255,0.3);}
.bc-s{font-size:10px;color:rgba(255,255,255,0.18);}
.bc-i.act{color:rgba(255,255,255,0.65);}
.ph-row{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;}
.ph-title{font-size:20px;font-weight:600;color:#fff;letter-spacing:-0.3px;}
.ph-sub{font-size:12px;color:rgba(255,255,255,0.35);margin-top:3px;}
.ph-tag{font-size:10px;font-weight:600;color:#93C5FD;background:rgba(59,130,246,0.14);border:1px solid rgba(59,130,246,0.25);border-radius:20px;padding:4px 12px;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;}
.content{flex:1;padding:32px 40px 56px;max-width:1440px;width:100%;margin:0 auto;}
.upanel{background:var(--surf);border:1px solid var(--bdr);border-radius:var(--rml);padding:20px 24px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:24px;}
.ulabel{display:inline-flex;align-items:center;gap:8px;cursor:pointer;border:1px dashed var(--blueln);background:var(--bluelt);border-radius:var(--rmm);padding:9px 16px;transition:background 0.15s;user-select:none;}
.ulabel:hover{background:#D9E9FF;}
.ulabel svg{width:14px;height:14px;fill:var(--blue);flex-shrink:0;}
.ulabel span{font-size:13px;font-weight:500;color:var(--blue);}
.ulabel input[type=file]{display:none;}
.fname{font-size:12px;color:var(--t3);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:280px;font-family:'DM Mono',monospace;}
.sep{width:1px;height:28px;background:var(--bdr);flex-shrink:0;}
.btn{display:inline-flex;align-items:center;gap:7px;padding:9px 18px;border:none;border-radius:var(--rmm);font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;white-space:nowrap;transition:opacity 0.15s,transform 0.15s;}
.btn:hover{opacity:0.85;}
.btn:active{transform:scale(0.98);}
.btn svg{width:14px;height:14px;flex-shrink:0;}
.btn-blue{background:var(--blue);color:#fff;}
.btn-green{background:var(--grn);color:#fff;}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
.kpi{background:var(--surf);border:1px solid var(--bdr);border-radius:var(--rml);padding:20px 22px;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;transition:box-shadow 0.18s;}
.kpi:hover{box-shadow:0 4px 20px rgba(23,87,194,0.09);}
.kpi-lbl{font-size:11px;font-weight:500;color:var(--t3);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;}
.kpi-val{font-size:34px;font-weight:600;color:var(--t1);line-height:1;letter-spacing:-1px;}
.kpi-meta{font-size:11px;color:var(--t3);margin-top:8px;}
.kpi-meta b{color:var(--t2);font-weight:500;}
.kpi-ico{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.kpi-ico svg{width:19px;height:19px;}
.kpi-ico.bl{background:var(--bluelt);}.kpi-ico.bl svg{fill:var(--blue);}
.kpi-ico.gn{background:var(--grnlt);}.kpi-ico.gn svg{fill:var(--grn);}
.kpi-ico.am{background:var(--amblt);}.kpi-ico.am svg{fill:var(--amb);}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px;flex-wrap:wrap;}
.sfld{position:relative;width:320px;}
.sfld svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);width:14px;height:14px;fill:var(--t3);pointer-events:none;}
.sfld input{width:100%;padding:9px 12px 9px 34px;border:1px solid var(--bdr);border-radius:var(--rmm);font-family:'DM Sans',sans-serif;font-size:13px;color:var(--t1);background:var(--surf);outline:none;transition:border-color 0.15s;}
.sfld input::placeholder{color:var(--t3);}
.sfld input:focus{border-color:var(--bluem);}
.tcard{background:var(--surf);border:1px solid var(--bdr);border-radius:var(--rml);overflow:hidden;}
.tcard-top{display:flex;align-items:center;justify-content:space-between;padding:16px 22px;border-bottom:1px solid var(--bdr);}
.tcard-ttl{font-size:13px;font-weight:600;color:var(--t1);display:flex;align-items:center;gap:8px;}
.tcard-ttl svg{width:15px;height:15px;fill:var(--t3);}
.row-ct{font-size:11px;font-weight:500;color:var(--t3);background:var(--bg);border:1px solid var(--bdr);border-radius:20px;padding:3px 10px;}
.twrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;}
thead tr{background:var(--navy);border-bottom:2px solid var(--navy3);}
thead th{
  padding:14px 16px;
  text-align:left;
  font-size:13px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:1px;
  color:#FFFFFF;
  white-space:nowrap;
}
thead th:first-child{padding-left:22px;}
tbody tr{border-bottom:1px solid var(--bdr);transition:background 0.12s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:var(--bluelt);}
tbody td{
  padding:14px 16px;
  color:var(--t2);
  vertical-align:middle;
  font-size:15px;
}
tbody td:first-child{padding-left:22px;}
.td-dt{
  font-family:'DM Mono',monospace;
  font-size:14px;
  font-weight:600;
  color:var(--t1);
  white-space:nowrap;
}
.td-s{
  font-size:15px;
  font-weight:600;
  color:var(--t1);
}
.td-ty{
  font-size:14px;
  font-weight:600;
  color:#334155;
}
.td-ac{
  max-width:220px;
  line-height:1.5;
  font-size:15px;
}
  .qbadge {
  background: transparent;
  color: #1e293b;
  padding: 0;
  border-radius: 0;
  font-weight: 600;
}
.dash-c{color:var(--bdr);font-size:18px;}
.erow td{padding:72px 22px !important;}
.einner{display:flex;flex-direction:column;align-items:center;gap:10px;}
.eico{opacity:0.22;}.eico svg{width:40px;height:40px;fill:var(--t3);}
.ettl{font-size:14px;font-weight:600;color:var(--t3);}
.esub{font-size:12px;color:var(--t3);}
.footer{background:var(--navy);padding:14px 40px;display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(255,255,255,0.05);}
.fl{font-size:11px;color:rgba(255,255,255,0.22);}
.fr{font-size:11px;color:rgba(255,255,255,0.16);}
@media(max-width:900px){.kpi-row{grid-template-columns:repeat(2,1fr);}.topbar,.content,.ph,.footer{padding-left:20px;padding-right:20px;}}
@media(max-width:600px){.kpi-row{grid-template-columns:1fr;}.toolbar{flex-direction:column;align-items:stretch;}.sfld{width:100%;}.ph-row{flex-direction:column;align-items:flex-start;}}
`;

const Ico = {
  Logo:   () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M3 18V7l7-5 7 5v11H12v-5H8v5H3z"/></svg>,
  Upload: () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M9 13V7.41L6.7 9.7 5.3 8.3 10 3.6l4.7 4.7-1.4 1.4L11 7.41V13H9zM4 16h12v-3h2v3a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-3h2v3z"/></svg>,
  Excel:  () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M11 2 4 3.5v13L11 18l5-1V3l-5-1zm-1 12.5L8 12l-1.5 2.5-1.5-.5L7 11 5 8.5l1.5-.5L8 10.5 10 8l1.5.5L9.5 11 12 14l-2 .5zM13 15V5l2 .5v9L13 15z"/></svg>,
  Search: () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M12.9 11.5h-.8l-.3-.3A6 6 0 1 0 8 14a6 6 0 0 0 3.7-1.3l.3.3v.8l4.3 4.2 1.3-1.3-4.2-4.2zm-5 0A4 4 0 1 1 12 7.5a4 4 0 0 1-4 4z"/></svg>,
  Hat:    () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 2a8 8 0 0 0-7.93 7H4a6 6 0 0 1 12 0h1.93A8 8 0 0 0 10 2zm-8 9v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3H2z"/></svg>,
  List:   () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2 4h2v2H2V4zm4 0h12v2H6V4zm-4 5h2v2H2V9zm4 0h12v2H6V9zm-4 5h2v2H2v-2zm4 0h12v2H6v-2z"/></svg>,
  Box:    () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 1 1 5.5v9L10 19l9-4.5v-9L10 1zm0 2.24 6.5 3.26L10 9.76 3.5 6.5 10 3.24zM2 7.36l7 3.5v7l-7-3.5v-7zm9 10.5v-7l7-3.5v7l-7 3.5z"/></svg>,
  File:   () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M12 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 1.5L16.5 9H11V3.5z"/></svg>,
  Layers: () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 2 1 7l9 5 9-5-9-5zm0 10.17L2.19 8 1 8.67 10 14l9-5.33-1.19-.67L10 12.17z"/></svg>,
  Inbox:  () => <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4zm2 7v4h12v-4h-3l-1.5 2h-3L7 11H4zm0-7v5h3.5l1.5 2h2l1.5-2H16V4H4z"/></svg>,
};

export default function App() {
  const [file, setFile]       = useState(null);
  const [records, setRecords] = useState([]);
  const [search, setSearch]   = useState("");

  const uploadPDF = async () => {
    if (!file) { alert("Please select a PDF file"); return; }
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res  = await fetch("http://127.0.0.1:8000/upload-pdf", { method: "POST", body: fd });
      const data = await res.json();
      console.log(data.records)
      setRecords(
  data.records.map((record) => ({
    date: record.date,
    site: data.site,
    contractor: record.contractor,
    type: data.type_of_work,
    skilled: record.skilled,
    unskilled: record.unskilled,
    activity: record.activity,
    quantity: record.quantity,
    remark: record.remark,
  }))
);
      alert("PDF uploaded successfully");
    } catch (err) { console.error(err); alert("Upload failed"); }
  };

  const exportToExcel = async () => {
    const wb = new ExcelJS.Workbook();
    const ws = wb.addWorksheet("DPR Report");
    ws.mergeCells("A1:A2"); ws.mergeCells("B1:B2"); ws.mergeCells("C1:C2");
    ws.mergeCells("D1:D2"); ws.mergeCells("E1:F1"); ws.mergeCells("G1:G2");
    ws.mergeCells("H1:H2"); ws.mergeCells("I1:I2");
    ws.getRow(1).height = 25; ws.getRow(2).height = 25;
    ws.getCell("A1").value = "DATE";           ws.getCell("B1").value = "SITE";
    ws.getCell("C1").value = "Contractor Name"; ws.getCell("D1").value = "Type of Work";
    ws.getCell("E1").value = "Total No of Labour"; ws.getCell("G1").value = "ACTIVITY";
    ws.getCell("H1").value = "QUANTITY";        ws.getCell("I1").value = "REMARK";
    ws.getCell("E2").value = "Skilled";         ws.getCell("F2").value = "Unskilled";
    ws.columns = [
      {width:18},{width:20},{width:25},{width:18},
      {width:12},{width:12},{width:30},{width:15},{width:20},
    ];
    [1,2].forEach((n) => {
      ws.getRow(n).font      = { bold: true, size: 12 };
      ws.getRow(n).alignment = { vertical: "middle", horizontal: "center" };
    });
    let ri = 3;
    records.forEach((row) => {
      const vals = [
        row.date,row.site,row.contractor,row.type,row.skilled,row.unskilled,row.activity,row.quantity,row.remark || "-"];
      ["A","B","C","D","E","F","G","H","I"].forEach((col,i) => {
        ws.getCell(`${col}${ri}`).value = vals[i];
      });
      ri++;
    });
    ws.eachRow((row) => {
      row.eachCell((cell) => {
        cell.border    = {top:{style:"thin"},left:{style:"thin"},bottom:{style:"thin"},right:{style:"thin"}};
        cell.alignment = {vertical:"middle",horizontal:"center",wrapText:true};
      });
    });
    saveAs(new Blob([await wb.xlsx.writeBuffer()]), "DPR_Report.xlsx");
  };

  const uniqueContractors = [
  ...new Map(
    records.map(r => [r.contractor, r])
  ).values()
];

const totalSkilled = uniqueContractors.reduce(
  (sum, r) => sum + Number(r.skilled || 0),
  0
);

const totalUnskilled = uniqueContractors.reduce(
  (sum, r) => sum + Number(r.unskilled || 0),
  0
);

const totalLabourers =
  totalSkilled + totalUnskilled;
  const totalQuantity  = records.reduce((s,r) => s + Number(r.quantity || 0), 0);
  const currentSite =
  records.length > 0
    ? records[0].site
    : "No Site";

  const filtered = useMemo(() => {
    if (!search.trim()) return records;
    const q = search.toLowerCase();
    return records.filter((r) =>
      [r.site, r.contractor, r.activity].some((v) => v && v.toLowerCase().includes(q))
    );
  }, [records, search]);

  const today = new Date().toLocaleDateString("en-GB", {day:"2-digit",month:"short",year:"numeric"});

  return (
    <>
      <style>{CSS}</style>
      <div className="shell">

        <header className="topbar">
          <div className="tb-left">
            <div className="logomark"><Ico.Logo /></div>
            <div className="logo-div" />
            <div>
              <span className="logo-name">Srusti Engineers</span>
              <span className="logo-sub">Daily progress dashboard</span>
            </div>
          </div>
          <div className="tb-right">

</div>
        </header>

        <div className="ph">
          <div className="bc">
            <span className="bc-i">Home</span>
            <span className="bc-s">›</span>
            <span className="bc-i">Reports</span>
            <span className="bc-s">›</span>
            <span className="bc-i act">Daily Progress Report</span>
          </div>
          <div className="ph-row">
            <div>
              <div className="ph-title">Daily Progress Report</div>
              <div className="ph-sub">Last updated: {today}</div>
            </div>
          </div>
        </div>

        <main className="content">

          <div className="upanel">
            <label className="ulabel">
              <Ico.File />
              <span>{file ? "Change file" : "Select PDF"}</span>
              <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
            </label>
            <span className="fname">{file ? file.name : "No file selected"}</span>
            <div className="sep" />
            <button className="btn btn-blue" onClick={uploadPDF}>
              <Ico.Upload /> Upload PDF
            </button>
            <button className="btn btn-green" onClick={exportToExcel}>
              <Ico.Excel /> Export to Excel
            </button>
          </div>
          <div className="kpi-row">

  <div className="kpi">
    <div>
      <div className="kpi-lbl">Site</div>
      <div
        className="kpi-val"
        style={{
          fontSize: "24px",
          lineHeight: "1.2",
        }}
      >
        {currentSite}
      </div>
      <div className="kpi-meta">
        Project Location
      </div>
    </div>

    <div className="kpi-ico bl">
      <Ico.Layers />
    </div>
  </div>

  <div className="kpi">
    <div>
      <div className="kpi-lbl">Total Labourers</div>
      <div className="kpi-val">{totalLabourers}</div>
      <div className="kpi-meta">
        Total workforce on site
        </div>
    </div>

    <div className="kpi-ico bl">
      <Ico.Hat />
    </div>
  </div>
  <div className="kpi">
  <div>
    <div className="kpi-lbl">Activities</div>
    <div className="kpi-val">{records.length}</div>
    <div className="kpi-meta">
      <b>{filtered.length}</b> matching current filter
    </div>
  </div>

  <div className="kpi-ico gn">
    <Ico.List />
  </div>
</div>

  <div className="kpi">
    <div>
      <div className="kpi-lbl">Total Quantity</div>
      <div className="kpi-val">
        {totalQuantity.toFixed(1)}
      </div>
      <div className="kpi-meta">
        Cumulative across all activities
      </div>
    </div>

    <div className="kpi-ico am">
      <Ico.Box />
    </div>
  </div>

</div>
          
            <div className="toolbar">
              <div className="sfld">
              <Ico.Search />
              <input
                type="text"
                placeholder="Search by site, contractor or activity..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="tcard">
            <div className="tcard-top">
              <span className="tcard-ttl"><Ico.Layers /> Progress Records</span>
              <span className="row-ct">{filtered.length} entries</span>
            </div>
            <div className="twrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
<th>Site</th>
<th>Contractor</th>
<th>Type of Work</th>
<th>Skilled</th>
<th>Unskilled</th>
<th>Activity</th>
<th>Quantity</th>
<th>Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr className="erow">
                      <td colSpan="9">
                        <div className="einner">
                          <div className="eico"><Ico.Inbox /></div>
                          <div className="ettl">{records.length === 0 ? "No records loaded" : "No results found"}</div>
                          <div className="esub">{records.length === 0 ? "Upload a PDF report to populate the table." : "Try adjusting your search query."}</div>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filtered.map((row, i) => (
                      <tr key={i}>
                       <td className="td-dt">{row.date}</td>
<td className="td-s">{row.site}</td>
<td className="td-s">{row.contractor}</td>
<td className="td-ty">{row.type}</td>

<td>{row.skilled}</td>
<td>{row.unskilled}</td>

<td className="td-ac">{row.activity}</td>
<td><span className="qbadge">{row.quantity}</span></td>
<td className="td-ac">{row.remark || "—"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </main>

        <footer className="footer">
          <span className="fl">SiteOps Construction Management · Daily Progress Report System</span>
          <span className="fr">© {new Date().getFullYear()} All rights reserved</span>
        </footer>

      </div>
    </>
  );
}