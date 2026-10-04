// Render manuscript_content.json -> DOCX (Elsevier / Talanta submission layout).
// usage: node render_docx.js content.json out.docx [--no-lines]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, Footer, PageNumber, LineNumberRestartFormat, TabStopType, ShadingType, PageBreak,
  LevelFormat,
} = require("docx");

const [, , inPath, outPath, ...flags] = process.argv;
const C = JSON.parse(fs.readFileSync(inPath, "utf8"));
const FONT = "Times New Roman";
const SZ = 24; // 12 pt
const LINE = flags.includes("--single") ? 276 : 480; // double spacing for review copy
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1440; // A4, 1-inch margins
const TEXT_W = PAGE_W - 2 * MARGIN;

// inline markup: **bold**, *italic*, ^{sup}, _{sub}
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|\^\{[^}]+\}|_\{[^}]+\})/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: SZ, ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, size: SZ, ...base }));
    else if (t.startsWith("*")) out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: FONT, size: SZ, ...base }));
    else if (t.startsWith("^")) out.push(new TextRun({ text: t.slice(2, -1), superScript: true, font: FONT, size: SZ, ...base }));
    else out.push(new TextRun({ text: t.slice(2, -1), subScript: true, font: FONT, size: SZ, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: SZ, ...base }));
  return out;
}

const P = (text, opts = {}) => new Paragraph({
  children: runs(text, opts.run || {}), alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { line: opts.line || LINE, after: opts.after ?? 120, before: opts.before ?? 0 },
  indent: opts.indent, keepNext: opts.keepNext,
});

const H = (text, level) => new Paragraph({
  heading: level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: FONT, size: SZ, bold: level < 3, italics: level === 3, color: "000000" })],
  spacing: { line: LINE, before: 240, after: 120 }, keepNext: true,
});

function equation(text, num) {
  return new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: TEXT_W / 2 }, { type: TabStopType.RIGHT, position: TEXT_W }],
    children: [new TextRun({ text: "\t", font: FONT, size: SZ }),
      ...runs(text, { font: "Cambria Math" }),
      new TextRun({ text: `\t(${num})`, font: FONT, size: SZ })],
    spacing: { line: LINE, before: 60, after: 60 },
  });
}

function figure(b) {
  const buf = fs.readFileSync(b.path);
  // read PNG size from IHDR
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const maxW = (b.width_in || 6.3) * 96; // px at 96 dpi
  const scale = maxW / w;
  return [
    new Paragraph({ children: [new ImageRun({ data: buf, type: "png", transformation: { width: Math.round(w * scale), height: Math.round(h * scale) } })],
      alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true }),
    P(b.caption, { line: 276, after: 240, run: { size: 20 } }),
  ];
}

function table(b) {
  const rows = b.rows; // array of arrays; first row header
  const ncol = rows[0].length;
  const firstW = b.first_col_w || Math.round(TEXT_W * (ncol > 8 ? 0.16 : 0.22));
  const otherW = Math.floor((TEXT_W - firstW) / (ncol - 1));
  const widths = [firstW, ...Array(ncol - 1).fill(otherW)];
  const total = widths.reduce((a, c) => a + c, 0);
  const fsz = ncol > 10 ? 14 : ncol > 7 ? 16 : 18;
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const line = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
  const tr = rows.map((r, i) => new TableRow({
    tableHeader: i === 0,
    children: r.map((cell, j) => new TableCell({
      width: { size: widths[j], type: WidthType.DXA },
      borders: { top: i === 0 ? line : none, bottom: (i === 0 || i === rows.length - 1) ? line : none, left: none, right: none },
      margins: { top: 30, bottom: 30, left: 60, right: 60 },
      shading: b.highlight_rows && b.highlight_rows.includes(i) ? { type: ShadingType.CLEAR, fill: "E8F0FB", color: "auto" } : undefined,
      children: [new Paragraph({ alignment: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 240 },
        children: runs(String(cell), { size: fsz, bold: i === 0 }) })],
    })),
  }));
  const out = [P(b.caption, { line: 276, after: 60, run: { size: 20 }, keepNext: true }),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: tr })];
  if (b.note) out.push(P(b.note, { line: 276, after: 240, run: { size: 18 } }));
  else out.push(P("", { after: 120 }));
  return out;
}

const children = [];
// ---------- title page
const M = C.meta;
children.push(new Paragraph({ children: runs(M.title, { bold: true, size: 32 }), alignment: AlignmentType.CENTER, spacing: { line: 360, after: 240 } }));
children.push(P(M.authors, { align: AlignmentType.CENTER, after: 120 }));
for (const a of M.affiliations) children.push(P(a, { align: AlignmentType.CENTER, after: 60, run: { size: 20 } }));
children.push(P(M.corresponding, { align: AlignmentType.LEFT, before: 240, run: { size: 20 } }));
if (M.word_count) children.push(P(M.word_count, { align: AlignmentType.LEFT, run: { size: 20 } }));
children.push(new Paragraph({ children: [new PageBreak()] }));
// ---------- abstract, keywords
children.push(H("Abstract", 1));
for (const para of M.abstract) children.push(P(para));
children.push(P(`**Keywords:** ${M.keywords.join("; ")}`, { before: 120 }));
children.push(new Paragraph({ children: [new PageBreak()] }));
// ---------- body
for (const b of C.blocks) {
  if (b.type === "h1") children.push(H(b.text, 1));
  else if (b.type === "h2") children.push(H(b.text, 2));
  else if (b.type === "h3") children.push(H(b.text, 3));
  else if (b.type === "p") children.push(P(b.text));
  else if (b.type === "eq") children.push(equation(b.text, b.num));
  else if (b.type === "fig") children.push(...figure(b));
  else if (b.type === "table") children.push(...table(b));
  else if (b.type === "pagebreak") children.push(new Paragraph({ children: [new PageBreak()] }));
  else if (b.type === "bullets") for (const t of b.items) children.push(new Paragraph({ children: runs(t), numbering: { reference: "bul", level: 0 }, spacing: { line: LINE, after: 60 } }));
  else throw new Error("unknown block " + b.type);
}
// ---------- references
children.push(H("References", 1));
for (const r of C.references) children.push(P(r, { align: AlignmentType.LEFT, line: LINE, after: 60, indent: { left: 400, hanging: 400 } }));

const doc = new Document({
  creator: "Authors", title: M.title, description: "Manuscript submitted to Talanta",
  styles: { default: { document: { run: { font: FONT, size: SZ } } } },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: {
      page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
      lineNumbers: flags.includes("--no-lines") ? undefined : { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS, distance: 300 },
    },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, suppressLineNumbers: true, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("wrote", outPath); });
