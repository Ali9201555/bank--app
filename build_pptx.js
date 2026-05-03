// Simple progress meeting deck for Project 1 — 4 slides.
// Run: node build_pptx.js

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Project 1 Progress Meeting";
pres.author = "Ali Alfatin";

const BG = "0F1824";      // deep banking navy
const PANEL = "1A2435";
const INK = "E6ECF5";
const MUTED = "9AA7BB";
const GOLD = "F5C542";    // bank-gold accent
const BLUE = "2D6CDF";
const GREEN = "29CC74";
const PURPLE = "5E4BD5";
const ORANGE = "C98A2E";
const RED = "C0392B";

function newSlide() {
  const s = pres.addSlide();
  s.background = { color: BG };
  return s;
}

function heading(slide, text, subtitle) {
  slide.addText(text, {
    x: 0.6, y: 0.5, w: 12, h: 0.8,
    fontSize: 36, bold: true, color: INK, fontFace: "Calibri", margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6, y: 1.2, w: 12, h: 0.4,
      fontSize: 16, color: MUTED, italic: true, fontFace: "Calibri", margin: 0
    });
  }
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 1.75, w: 1.5, h: 0,
    line: { color: GOLD, width: 3 }
  });
}

// ============================================================
// Slide 1 — Title
// ============================================================
{
  const s = newSlide();
  s.addText("Project 1", {
    x: 0.6, y: 2.2, w: 12, h: 0.6,
    fontSize: 20, color: GOLD, bold: true, fontFace: "Calibri", charSpacing: 6, margin: 0
  });
  s.addText("Bank App", {
    x: 0.6, y: 2.8, w: 12, h: 1.4,
    fontSize: 72, bold: true, color: INK, fontFace: "Calibri", margin: 0
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 4.4, w: 2, h: 0,
    line: { color: GOLD, width: 3 }
  });
  s.addText("Improved from Lab 9  ·  Progress Meeting", {
    x: 0.6, y: 4.5, w: 12, h: 0.5,
    fontSize: 20, color: MUTED, fontFace: "Calibri", italic: true, margin: 0
  });
  s.addText("Ali Alfatin  ·  CSCI 2680", {
    x: 0.6, y: 6.7, w: 12, h: 0.4,
    fontSize: 14, color: MUTED, fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// Slide 2 — The idea + sketch
// ============================================================
{
  const s = newSlide();
  heading(s, "The idea", "A banking GUI built on top of Lab 9's classes");

  s.addText(
    "I'm taking Lab 9's Account and SavingAccount classes and wrapping " +
    "them in a PyQt6 desktop app. A table lists every account, buttons " +
    "let the user open, deposit, withdraw, or close. Every transaction " +
    "is saved to a CSV file and shown in a history log.",
    {
      x: 0.6, y: 2.1, w: 6, h: 3.5,
      fontSize: 16, color: INK, fontFace: "Calibri", paraSpaceAfter: 10, margin: 0
    }
  );

  drawSketch(s, 7.2, 2.0, 5.5, 4.7);
  s.addText("Rough sketch of the main window", {
    x: 7.2, y: 6.75, w: 5.5, h: 0.35,
    fontSize: 11, color: MUTED, italic: true, align: "center", fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// Slide 3 — What it will do
// ============================================================
{
  const s = newSlide();
  heading(s, "What it will do", "Planned features");

  const features = [
    "Three account types — Account, SavingAccount, CheckingAccount (new subclass)",
    "Open, close, deposit, and withdraw from any account",
    "Interest on saving accounts after every 5 deposits (2%)",
    "Overdraft allowance + fee on checking accounts",
    "Total at the bank shown at the bottom of the window",
    "Transaction history — per account or across the whole bank",
    "Data saved in CSV files so it survives a restart",
    "Input validation + error messages for bad numbers or empty names",
    "Python + PyQt6 with MVC file structure (models / views / controllers)",
  ];

  features.forEach((f, i) => {
    const y = 2.15 + i * 0.5;
    s.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.05, w: 0.32, h: 0.32,
      fill: { color: GOLD }, line: { color: GOLD }
    });
    s.addText(`${i + 1}`, {
      x: 0.7, y: y + 0.05, w: 0.32, h: 0.32,
      fontSize: 13, bold: true, color: BG, align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });
    s.addText(f, {
      x: 1.2, y, w: 11.5, h: 0.42,
      fontSize: 14, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
    });
  });
}

// ============================================================
// Slide 4 — Questions for the meeting
// ============================================================
{
  const s = newSlide();
  heading(s, "Questions for the meeting", "What I'd like feedback on");

  const questions = [
    "Is adding the CheckingAccount subclass enough extra OOP work?",
    "Should I also log interest events to the transaction history?",
    "Any other edge cases I should make sure to handle?",
    "Is the CSV format fine, or should I switch to SQLite?",
  ];

  questions.forEach((q, i) => {
    const y = 2.3 + i * 0.9;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y, w: 12, h: 0.7,
      fill: { color: PANEL }, line: { color: "2A3449", width: 1 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y, w: 0.1, h: 0.7,
      fill: { color: GOLD }, line: { color: GOLD }
    });
    s.addText(q, {
      x: 1.0, y, w: 11.5, h: 0.7,
      fontSize: 16, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
    });
  });

  s.addText("AI was used to help generate some boilerplate code — disclosed as required.", {
    x: 0.7, y: 6.7, w: 12, h: 0.4,
    fontSize: 11, color: MUTED, italic: true, fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// SKETCH — banking window wireframe
// ============================================================
function drawSketch(slide, x, y, w, h) {
  // Window frame
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: PANEL }, line: { color: "2A3449", width: 2 }
  });
  // Title bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.35,
    fill: { color: "0F1824" }, line: { color: "0F1824" }
  });
  slide.addText("Bank — Project 1", {
    x: x + 0.15, y: y + 0.02, w: 4, h: 0.3,
    fontSize: 10, bold: true, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
  });

  // Menu bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y: y + 0.35, w, h: 0.22, fill: { color: "121B2A" }, line: { color: "121B2A" }
  });
  slide.addText("File   Tools", {
    x: x + 0.15, y: y + 0.35, w: 3, h: 0.22,
    fontSize: 8, color: MUTED, fontFace: "Calibri", valign: "middle", margin: 0
  });

  // Main content split
  const bodyY = y + 0.7;
  const bodyH = h - 0.9;
  const leftW = w * 0.68;
  const rightW = w * 0.27;
  const rightX = x + leftW + 0.1;

  // Left — account table
  slide.addText("Accounts", {
    x: x + 0.2, y: bodyY, w: 3, h: 0.3,
    fontSize: 10, bold: true, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
  });

  const tableY = bodyY + 0.35;
  const tableH = bodyH - 0.9;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.2, y: tableY, w: leftW - 0.3, h: tableH,
    fill: { color: BG }, line: { color: "2A3449", width: 1 }
  });

  // Table header
  const headerH = 0.3;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.2, y: tableY, w: leftW - 0.3, h: headerH,
    fill: { color: "162233" }, line: { color: "162233" }
  });
  const headers = ["Type", "Name", "Balance"];
  const colW = (leftW - 0.3) / 3;
  headers.forEach((h, i) => {
    slide.addText(h, {
      x: x + 0.25 + i * colW, y: tableY, w: colW - 0.1, h: headerH,
      fontSize: 9, bold: true, color: GOLD, fontFace: "Calibri", valign: "middle", margin: 0
    });
  });

  // Table rows (sample data)
  const rows = [
    ["Checking", "John", "$115.00"],
    ["Saving", "Jane", "$357.00"],
    ["Account", "Rekha", "$50.75"],
    ["Saving", "Tao", "$178.64"],
  ];
  const rowH = 0.32;
  rows.forEach((row, r) => {
    const ry = tableY + headerH + r * rowH;
    if (r % 2 === 1) {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.2, y: ry, w: leftW - 0.3, h: rowH,
        fill: { color: "14202F" }, line: { color: "14202F" }
      });
    }
    row.forEach((cell, i) => {
      slide.addText(cell, {
        x: x + 0.25 + i * colW, y: ry, w: colW - 0.1, h: rowH,
        fontSize: 9, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
      });
    });
  });

  // Total line under the table
  slide.addText("Total at the bank: $701.39", {
    x: x + 0.2, y: tableY + tableH + 0.1, w: leftW - 0.3, h: 0.3,
    fontSize: 10, bold: true, color: GOLD, fontFace: "Calibri", align: "right", valign: "middle", margin: 0
  });

  // Right — action panel
  slide.addText("Actions", {
    x: rightX, y: bodyY, w: rightW, h: 0.3,
    fontSize: 10, bold: true, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
  });

  const buttons = [
    { label: "Open Account", color: GREEN },
    { label: "Deposit", color: BLUE },
    { label: "Withdraw", color: ORANGE },
    { label: "View History", color: PURPLE },
    { label: "Close Account", color: RED },
  ];
  const btnTop = bodyY + 0.35;
  const btnH = 0.4;
  const btnGap = 0.12;
  buttons.forEach((b, i) => {
    const by = btnTop + i * (btnH + btnGap);
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: rightX, y: by, w: rightW, h: btnH,
      fill: { color: b.color }, line: { color: b.color }, rectRadius: 0.06
    });
    slide.addText(b.label, {
      x: rightX, y: by, w: rightW, h: btnH,
      fontSize: 10, bold: true, color: "FFFFFF", align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });
  });
}

pres.writeFile({ fileName: "Project1_Progress_Meeting.pptx" })
  .then(file => console.log("Wrote:", file))
  .catch(err => { console.error("FAILED:", err); process.exit(1); });
