import sys
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from nicegui import ui
import json
from datetime import datetime
import subprocess
import threading
import asyncio
from services.email_service import EmailService
from services.whatsapp_service import WhatsAppService
from services.ai_post_service import AIPostService
from analytics_tracker import (
    increment_emails_sent,
    increment_whatsapp_sent,
    increment_ai_posts_generated,
    get_analytics,
)


# ── Global state ──────────────────────────────────────────────────────────────
class AppState:
    def __init__(self):
        self.scheduler_running = False
        self.last_post_time = None
        self.total_posts = 0
        self.current_page = "Dashboard"
        self.email_count = 0
        self.whatsapp_count = 0
        self.ai_post_count = 0


state = AppState()


# ── Data helpers ──────────────────────────────────────────────────────────────
def load_contacts():
    if os.path.exists("data/contacts.json"):
        with open("data/contacts.json", "r") as f:
            return json.load(f)
    return []


def save_contacts(contacts):
    os.makedirs("data", exist_ok=True)
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)


def format_status(status):
    if status:
        return "🟢 Active" if status else "🔴 Inactive"
    return "⚪ Unknown"


def get_analytics_data():
    analytics = get_analytics()
    state.email_count = analytics["emails_sent"]
    state.whatsapp_count = analytics["whatsapp_messages_sent"]
    state.ai_post_count = analytics["ai_posts_generated"]
    try:
        if os.path.exists("data/post_history.json"):
            with open("data/post_history.json", "r") as f:
                posts = json.load(f)
                if posts:
                    state.last_post_time = posts[-1]["timestamp"]
    except:
        pass
    return {
        "emails_sent": analytics["emails_sent"],
        "whatsapp_messages": analytics["whatsapp_messages_sent"],
        "ai_posts_generated": analytics["ai_posts_generated"],
        "scheduler_status": state.scheduler_running,
    }


# ── CSS injection ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Epilogue:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  /* ── Reset & base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    /* Base surfaces */
    --bg-base:       #0a0a0f;
    --bg-panel:      #0f0f18;
    --bg-card:       #13131f;
    --bg-elevated:   #1a1a2a;
    --bg-input:      #16162280;

    /* Borders */
    --border:        rgba(255,255,255,0.06);
    --border-hover:  rgba(255,255,255,0.12);
    --border-gold:   rgba(251,191,36,0.35);

    /* Primary accent — Electric Amber/Gold */
    --gold:          #f59e0b;
    --gold-bright:   #fbbf24;
    --gold-dim:      rgba(245,158,11,0.12);
    --gold-glow:     rgba(245,158,11,0.06);

    /* Secondary accent — Cobalt */
    --cobalt:        #60a5fa;
    --cobalt-dim:    rgba(96,165,250,0.12);

    /* State colors */
    --emerald:       #10b981;
    --emerald-dim:   rgba(16,185,129,0.12);
    --rose:          #f43f5e;
    --rose-dim:      rgba(244,63,94,0.12);
    --violet:        #8b5cf6;
    --violet-dim:    rgba(139,92,246,0.12);
    --amber:         #f59e0b;
    --amber-dim:     rgba(245,158,11,0.12);

    /* Typography */
    --text-primary:  #f0f0f8;
    --text-secondary:#a0a0bc;
    --text-muted:    #50506a;
    --text-dim:      #30304a;

    /* Geometry */
    --radius-xs:     4px;
    --radius-sm:     8px;
    --radius-md:     12px;
    --radius-lg:     18px;
    --radius-xl:     24px;

    /* Shadows */
    --shadow-sm:     0 2px 8px rgba(0,0,0,0.4);
    --shadow-md:     0 4px 20px rgba(0,0,0,0.5);
    --shadow-lg:     0 8px 40px rgba(0,0,0,0.6);
    --shadow-gold:   0 0 24px rgba(245,158,11,0.15);

    /* Fonts */
    --font-display:  'Outfit', sans-serif;
    --font-body:     'Epilogue', sans-serif;
    --font-mono:     'Fira Code', monospace;
  }

  /* ════════════════════════════════════════
     GLOBAL RESETS — force dark everywhere
  ════════════════════════════════════════ */
  body, html {
    background: var(--bg-base) !important;
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Force ALL quasar/nicegui components to inherit dark */
  .q-page, .q-page-container,
  .nicegui-content, .nicegui-column {
    background: var(--bg-base) !important;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: rgba(245,158,11,0.2);
    border-radius: 99px;
  }
  ::-webkit-scrollbar-thumb:hover { background: rgba(245,158,11,0.4); }

  /* ════════════════════════════════════════
     LAYOUT
  ════════════════════════════════════════ */
  .app-shell {
    display: flex;
    min-height: 100vh;
    width: 100vw;
    overflow: hidden;
    background: var(--bg-base);
  }

  /* ════════════════════════════════════════
     SIDEBAR
  ════════════════════════════════════════ */
  .sidebar {
    width: 256px;
    min-width: 256px;
    background: var(--bg-panel);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 0;
    position: fixed;
    top: 0; left: 0;
    height: 100vh;
    z-index: 50;
    overflow-y: auto;
    overflow-x: hidden;
  }

  /* Subtle vertical grain texture on sidebar */
  .sidebar::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(255,255,255,0.005) 2px,
      rgba(255,255,255,0.005) 4px
    );
    pointer-events: none;
  }

  .sidebar-brand {
    padding: 24px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
  }

  .brand-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(245,158,11,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
    position: relative;
  }

  .brand-wordmark {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 16px;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 3px;
  }

  .brand-tag {
    font-family: var(--font-mono);
    font-size: 9.5px;
    color: var(--gold);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.8;
  }

  .nav-section {
    padding: 16px 12px;
    flex: 1;
  }

  .nav-label {
    font-family: var(--font-mono);
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0 10px;
    margin-bottom: 10px;
    display: block;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    margin-bottom: 2px;
    transition: all 0.16s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid transparent;
    text-decoration: none;
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 13.5px;
    font-weight: 500;
    position: relative;
    overflow: hidden;
    letter-spacing: 0.01em;
  }

  .nav-item::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 0;
    background: var(--gold);
    border-radius: 0 2px 2px 0;
    transition: width 0.16s ease;
  }

  .nav-item:hover {
    background: rgba(245,158,11,0.05);
    border-color: rgba(245,158,11,0.10);
    color: var(--text-secondary);
  }

  .nav-item.active {
    background: var(--gold-dim);
    border-color: var(--border-gold);
    color: var(--gold-bright);
    box-shadow: 0 0 20px rgba(245,158,11,0.08);
  }

  .nav-item.active::before { width: 3px; }

  .nav-icon {
    font-size: 17px;
    opacity: 0.85;
    flex-shrink: 0;
  }

  /* Sidebar status footer */
  .sidebar-footer {
    padding: 12px;
    border-top: 1px solid var(--border);
  }

  .status-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 16px;
  }

  .status-pill-title {
    font-family: var(--font-mono);
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
  }

  .status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--text-secondary);
  }

  .status-row:last-child { margin-bottom: 0; }

  .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .dot-green {
    background: var(--emerald);
    box-shadow: 0 0 8px var(--emerald);
    animation: blink 2.4s ease-in-out infinite;
  }

  .dot-red {
    background: var(--rose);
    box-shadow: 0 0 6px var(--rose);
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* ════════════════════════════════════════
     MAIN CONTENT
  ════════════════════════════════════════ */
  .main-content {
    margin-left: 256px;
    flex: 1;
    min-height: 100vh;
    background: var(--bg-base);
    overflow-y: auto;
    overflow-x: hidden;
  }

  /* ════════════════════════════════════════
     TOPBAR
  ════════════════════════════════════════ */
  .topbar {
    height: 60px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    position: sticky;
    top: 0;
    z-index: 40;
  }

  .topbar-title {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .topbar-pill {
    font-family: var(--font-mono);
    font-size: 10px;
    background: var(--gold-dim);
    color: var(--gold);
    border: 1px solid rgba(245,158,11,0.2);
    padding: 3px 8px;
    border-radius: var(--radius-xs);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .topbar-actions { display: flex; gap: 8px; align-items: center; }

  /* ════════════════════════════════════════
     PAGE BODY
  ════════════════════════════════════════ */
  .page-body {
    padding: 28px 32px;
    max-width: 1300px;
  }

  /* ════════════════════════════════════════
     STAT CARDS
  ════════════════════════════════════════ */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }

  .stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 22px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
  }

  /* Top shimmer line */
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 16px; right: 16px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-line, rgba(255,255,255,0.12)), transparent);
  }

  /* Background glow blob */
  .stat-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    background: radial-gradient(circle, var(--accent-glow, rgba(255,255,255,0.03)) 0%, transparent 70%);
    pointer-events: none;
  }

  .stat-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-hover);
    box-shadow: var(--shadow-md);
  }

  /* Accent variants */
  .stat-card.gold   { --accent-line: rgba(245,158,11,0.4);  --accent-glow: rgba(245,158,11,0.08);  --accent: var(--gold);    --accent-bg: var(--gold-dim); }
  .stat-card.cobalt { --accent-line: rgba(96,165,250,0.4);  --accent-glow: rgba(96,165,250,0.08);  --accent: var(--cobalt);  --accent-bg: var(--cobalt-dim); }
  .stat-card.violet { --accent-line: rgba(139,92,246,0.4);  --accent-glow: rgba(139,92,246,0.08);  --accent: var(--violet);  --accent-bg: var(--violet-dim); }
  .stat-card.emerald{ --accent-line: rgba(16,185,129,0.4);  --accent-glow: rgba(16,185,129,0.08);  --accent: var(--emerald); --accent-bg: var(--emerald-dim); }
  .stat-card.rose   { --accent-line: rgba(244,63,94,0.4);   --accent-glow: rgba(244,63,94,0.08);   --accent: var(--rose);    --accent-bg: var(--rose-dim); }

  .stat-icon-wrap {
    width: 40px; height: 40px;
    border-radius: var(--radius-sm);
    background: var(--accent-bg);
    border: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 18px;
  }

  .stat-value {
    font-family: var(--font-display);
    font-size: 32px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 5px;
    letter-spacing: -0.03em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }

  /* Smaller font for text values like "Active/Idle" */
  .stat-value.is-text {
    font-size: 20px;
    letter-spacing: -0.01em;
  }

  .stat-label {
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 2px;
    letter-spacing: 0.01em;
  }

  .stat-sub {
    font-size: 11.5px;
    color: var(--text-muted);
    font-family: var(--font-body);
  }

  /* ════════════════════════════════════════
     PANELS
  ════════════════════════════════════════ */
  .panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    position: relative;
  }

  .panel-header {
    padding: 18px 22px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.015);
  }

  .panel-title {
    font-family: var(--font-display);
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.01em;
  }

  .panel-body { padding: 22px; }

  /* ════════════════════════════════════════
     BUTTONS
  ════════════════════════════════════════ */
  .btn-primary {
    background: linear-gradient(135deg, #f59e0b, #f97316) !important;
    color: #0a0a0f !important;
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 4px 16px rgba(245,158,11,0.30) !important;
    text-transform: none !important;
    letter-spacing: 0.01em !important;
  }

  .btn-primary:hover {
    box-shadow: 0 6px 24px rgba(245,158,11,0.45) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.05) !important;
  }

  .btn-success {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #021a11 !important;
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.25) !important;
    transition: all 0.18s ease !important;
    text-transform: none !important;
    letter-spacing: 0.01em !important;
  }

  .btn-success:hover {
    box-shadow: 0 6px 22px rgba(16,185,129,0.40) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.05) !important;
  }

  .btn-danger {
    background: linear-gradient(135deg, #be123c, #f43f5e) !important;
    color: #fff !important;
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(244,63,94,0.25) !important;
    transition: all 0.18s ease !important;
    text-transform: none !important;
    letter-spacing: 0.01em !important;
  }

  .btn-danger:hover {
    box-shadow: 0 6px 22px rgba(244,63,94,0.40) !important;
    transform: translateY(-1px) !important;
  }

  .btn-ghost {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 12.5px !important;
    padding: 8px 16px !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    transition: all 0.16s ease !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
  }

  .btn-ghost:hover {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-hover) !important;
  }

  .btn-sm-danger {
    background: var(--rose-dim) !important;
    color: var(--rose) !important;
    font-family: var(--font-body) !important;
    font-size: 11.5px !important;
    padding: 5px 12px !important;
    border-radius: var(--radius-xs) !important;
    border: 1px solid rgba(244,63,94,0.20) !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: all 0.15s ease !important;
  }

  .btn-sm-danger:hover {
    background: rgba(244,63,94,0.22) !important;
    border-color: rgba(244,63,94,0.35) !important;
  }

  /* ════════════════════════════════════════
     QUASAR INPUT OVERRIDES — CRITICAL
  ════════════════════════════════════════ */
  /* Filled variant */
  .q-field--filled .q-field__control,
  .q-field--outlined .q-field__control {
    background: var(--bg-elevated) !important;
    border-radius: var(--radius-sm) !important;
  }

  .q-field--outlined .q-field__control {
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
  }

  .q-field--outlined.q-field--focused .q-field__control {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.10) !important;
  }

  .q-field--outlined:hover .q-field__control {
    border-color: rgba(255,255,255,0.14) !important;
  }

  .q-field__native,
  .q-field__input,
  .q-field__prefix,
  .q-field__suffix {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    caret-color: var(--gold) !important;
  }

  .q-field__label {
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
  }

  .q-field--focused .q-field__label,
  .q-field--float .q-field__label {
    color: var(--gold) !important;
    font-size: 11px !important;
  }

  .q-field__bottom { display: none !important; }

  /* Textarea */
  .q-textarea .q-field__native {
    min-height: 120px !important;
    resize: vertical !important;
  }

  /* ════════════════════════════════════════
     SELECT / DROPDOWN — CRITICAL FIX
  ════════════════════════════════════════ */
  /* The popup menu */
  .q-menu {
    background: #1a1a2e !important;
    border: 1px solid rgba(245,158,11,0.20) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 8px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04) !important;
    overflow: hidden !important;
    backdrop-filter: blur(20px) !important;
  }

  .q-list {
    background: transparent !important;
    padding: 6px !important;
  }

  .q-item {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-size: 13.5px !important;
    border-radius: var(--radius-xs) !important;
    min-height: 36px !important;
    padding: 0 10px !important;
    transition: all 0.12s ease !important;
  }

  .q-item:hover,
  .q-item--active {
    background: var(--gold-dim) !important;
    color: var(--gold-bright) !important;
  }

  .q-item__label {
    font-family: var(--font-body) !important;
    font-size: 13.5px !important;
    color: inherit !important;
  }

  /* The select trigger field */
  .q-field__append .q-icon {
    color: var(--text-muted) !important;
    transition: color 0.15s ease !important;
  }

  .q-field--focused .q-field__append .q-icon {
    color: var(--gold) !important;
  }

  /* Virtual scroll container inside dropdown */
  .q-virtual-scroll__content {
    background: transparent !important;
  }

  /* ════════════════════════════════════════
     TABS — CRITICAL: FIX WHITE BACKGROUND
  ════════════════════════════════════════ */
  .q-tabs {
    background: var(--bg-elevated) !important;
    border-radius: var(--radius-sm) !important;
    padding: 4px !important;
    min-height: 44px !important;
  }

  .q-tab {
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    min-height: 36px !important;
    padding: 0 18px !important;
    border-radius: var(--radius-xs) !important;
    transition: all 0.16s ease !important;
  }

  .q-tab:hover {
    color: var(--text-secondary) !important;
    background: rgba(255,255,255,0.04) !important;
  }

  .q-tab--active {
    color: var(--gold-bright) !important;
    background: var(--gold-dim) !important;
  }

  .q-tabs__indicator {
    display: none !important;
  }

  .q-tab__label { font-family: var(--font-body) !important; }

  /* Tab panels — THE KEY FIX for white background */
  .q-tab-panels {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
  }

  .q-tab-panel {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    padding: 24px !important;
  }

  /* The panel parent container */
  .q-panel, .q-panel-parent {
    background: var(--bg-card) !important;
  }

  /* ════════════════════════════════════════
     TOGGLE
  ════════════════════════════════════════ */
  .q-toggle__track {
    background: rgba(255,255,255,0.10) !important;
    border-radius: 99px !important;
  }

  .q-toggle__inner--truthy .q-toggle__track {
    background: rgba(245,158,11,0.30) !important;
  }

  .q-toggle__inner--truthy .q-toggle__thumb::before {
    background: var(--gold) !important;
    box-shadow: 0 0 8px rgba(245,158,11,0.5) !important;
  }

  /* ════════════════════════════════════════
     BADGE CHIPS
  ════════════════════════════════════════ */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: var(--radius-xs);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .badge-green  { background: var(--emerald-dim); color: var(--emerald); border: 1px solid rgba(16,185,129,0.22); }
  .badge-red    { background: var(--rose-dim);    color: var(--rose);    border: 1px solid rgba(244,63,94,0.22); }
  .badge-gold   { background: var(--gold-dim);    color: var(--gold);    border: 1px solid rgba(245,158,11,0.25); }
  .badge-cobalt { background: var(--cobalt-dim);  color: var(--cobalt);  border: 1px solid rgba(96,165,250,0.22); }

  /* ════════════════════════════════════════
     ACTIVITY CARDS
  ════════════════════════════════════════ */
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .activity-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px;
    transition: border-color 0.18s ease;
  }

  .activity-card:hover { border-color: var(--border-hover); }

  .activity-title {
    font-family: var(--font-display);
    font-size: 13.5px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 7px;
    letter-spacing: -0.01em;
  }

  .activity-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-family: var(--font-body);
    font-size: 12.5px;
    color: var(--text-secondary);
    margin-bottom: 7px;
    line-height: 1.55;
  }

  /* ════════════════════════════════════════
     CONTACT CARD
  ════════════════════════════════════════ */
  .contact-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    transition: all 0.18s ease;
  }

  .contact-card:hover {
    border-color: var(--border-hover);
    background: rgba(245,158,11,0.03);
  }

  .contact-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(245,158,11,0.25), rgba(139,92,246,0.25));
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    margin-right: 12px;
    flex-shrink: 0;
  }

  .contact-name {
    font-family: var(--font-body);
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 2px;
  }

  .contact-meta {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
  }

  /* ════════════════════════════════════════
     SCHEDULER BANNER
  ════════════════════════════════════════ */
  .scheduler-banner {
    background: linear-gradient(135deg,
      rgba(245,158,11,0.06) 0%,
      rgba(139,92,246,0.06) 100%
    );
    border: 1px solid rgba(245,158,11,0.18);
    border-radius: var(--radius-lg);
    padding: 22px 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    position: relative;
    overflow: hidden;
  }

  .scheduler-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(245,158,11,0.4), transparent);
  }

  /* ════════════════════════════════════════
     LOG BOX
  ════════════════════════════════════════ */
  .log-box {
    background: #060609;
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: var(--radius-md);
    padding: 16px;
    font-family: var(--font-mono);
    font-size: 11.5px;
    color: #a3e635;
    line-height: 1.75;
    max-height: 340px;
    overflow-y: auto;
  }

  .log-box .q-field__control { background: transparent !important; border: none !important; box-shadow: none !important; }
  .log-box .q-field__native  { color: #a3e635 !important; font-family: var(--font-mono) !important; font-size: 11.5px !important; }
  .log-box .q-field--outlined .q-field__control { border: none !important; }

  /* ════════════════════════════════════════
     POST PREVIEW
  ════════════════════════════════════════ */
  .post-preview {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    font-family: var(--font-body);
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.7;
  }

  /* ════════════════════════════════════════
     SECTION HEADINGS
  ════════════════════════════════════════ */
  .section-heading {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.025em;
    line-height: 1.2;
  }

  .section-sub {
    font-family: var(--font-body);
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 5px;
    line-height: 1.5;
  }

  /* ════════════════════════════════════════
     INFO ROWS (settings page)
  ════════════════════════════════════════ */
  .two-col-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }

  .info-row:last-child { border-bottom: none; }

  .info-key {
    font-family: var(--font-body);
    color: var(--text-muted);
    flex: 1;
    font-size: 12.5px;
  }

  .info-val {
    font-family: var(--font-mono);
    color: var(--text-primary);
    font-size: 12px;
    word-break: break-all;
    text-align: right;
  }

  /* ════════════════════════════════════════
     NOTIFICATION OVERRIDES
  ════════════════════════════════════════ */
  .q-notification {
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    backdrop-filter: blur(20px) !important;
  }

  .q-notification--positive {
    background: rgba(16,185,129,0.15) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    color: var(--text-primary) !important;
  }

  .q-notification--negative {
    background: rgba(244,63,94,0.15) !important;
    border: 1px solid rgba(244,63,94,0.3) !important;
    color: var(--text-primary) !important;
  }

  .q-notification--info {
    background: rgba(96,165,250,0.15) !important;
    border: 1px solid rgba(96,165,250,0.3) !important;
    color: var(--text-primary) !important;
  }

  .q-notification--warning {
    background: rgba(245,158,11,0.15) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    color: var(--text-primary) !important;
  }

  /* ════════════════════════════════════════
     SEPARATOR
  ════════════════════════════════════════ */
  .q-separator { background: var(--border) !important; }

  /* ════════════════════════════════════════
     RESPONSIVE
  ════════════════════════════════════════ */
  @media (max-width: 1100px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 700px)  {
    .stats-grid { grid-template-columns: 1fr; }
    .two-col, .two-col-info { grid-template-columns: 1fr; }
  }
</style>
"""


# ── Navigation helper ─────────────────────────────────────────────────────────
def navigate_to_page(page_name):
    state.current_page = page_name
    ui.run_javascript("location.reload();")


# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar_navigation():
    nav_items = [
        ("Dashboard",          "dashboard",    "Dashboard"),
        ("Email Sender",       "email",        "Email Sender"),
        ("WhatsApp Manager",   "chat",         "WhatsApp Manager"),
        ("AI Post Generator",  "auto_awesome", "AI Post Generator"),
        ("Settings",           "settings",     "Settings"),
    ]

    ui.html('''
        <div class="sidebar-brand">
          <div class="brand-icon">🤖</div>
          <div>
            <div class="brand-wordmark">AutoPilot</div>
            <div class="brand-tag">Social Media AI</div>
          </div>
        </div>
    ''')

    with ui.element('div').classes('nav-section'):
        ui.html('<span class="nav-label">Navigation</span>')
        for page_name, icon, label in nav_items:
            active = "active" if state.current_page == page_name else ""
            with ui.element('div').classes(f'nav-item {active}').on(
                'click', lambda p=page_name: navigate_to_page(p)
            ):
                ui.icon(icon).classes('nav-icon')
                ui.label(label)

    # Footer status
    is_running = state.scheduler_running
    dot_class  = "dot-green" if is_running else "dot-red"
    sched_text = "Running" if is_running else "Stopped"
    last_post  = state.last_post_time or "Never"
    if last_post != "Never" and len(last_post) > 19:
        last_post = last_post[:19].replace("T", " ")

    ui.html(f'''
        <div class="sidebar-footer">
          <div class="status-pill">
            <div class="status-pill-title">System Status</div>
            <div class="status-row">
              <div class="dot {dot_class}"></div>
              <span>Scheduler: <strong style="color:var(--text-primary);">{sched_text}</strong></span>
            </div>
            <div class="status-row" style="gap:8px;">
              <span style="font-size:12px;opacity:.7;">⏱</span>
              <span>Last: {last_post}</span>
            </div>
          </div>
        </div>
    ''')


# ── Top bar ───────────────────────────────────────────────────────────────────
TOPBAR_TITLES = {
    "Dashboard":         ("📊", "Dashboard",         "OVERVIEW"),
    "Email Sender":      ("📧", "Email Sender",       "COMPOSE"),
    "WhatsApp Manager":  ("💬", "WhatsApp Manager",   "MESSAGING"),
    "AI Post Generator": ("🤖", "AI Post Generator",  "AI"),
    "Settings":          ("⚙️",  "Settings",           "CONFIG"),
}

def topbar():
    icon, title, pill = TOPBAR_TITLES.get(state.current_page, ("", state.current_page, ""))
    with ui.element('div').classes('topbar'):
        ui.html(f'''
            <div class="topbar-title">
              <span>{icon}</span>
              <span>{title}</span>
              <span class="topbar-pill">{pill}</span>
            </div>
        ''')
        with ui.element('div').classes('topbar-actions'):
            ui.button(
                "↺ Refresh",
                on_click=lambda: ui.run_javascript("location.reload()")
            ).classes('btn-ghost')


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_page():
    analytics = get_analytics_data()

    with ui.element('div').classes('page-body'):

        # ── Stat cards ──────────────────────────────────────────────────────
        with ui.element('div').classes('stats-grid'):
            _stat_card("cobalt",  "email",       str(analytics["emails_sent"]),       "Emails Sent",       "Total delivered")
            _stat_card("emerald", "chat",         str(analytics["whatsapp_messages"]), "WhatsApp Messages", "Via WhatsApp API")
            _stat_card("violet",  "auto_awesome", str(analytics["ai_posts_generated"]),"AI Posts",          "Generated by AI")
            _sched_val = "Active" if analytics["scheduler_status"] else "Idle"
            _stat_card("gold",    "schedule",     _sched_val,                          "Scheduler",         "Automation state", text_val=True)

        # ── Scheduler panel ──────────────────────────────────────────────────
        with ui.element('div').classes('panel').style('margin-bottom:20px;'):
            with ui.element('div').classes('panel-header'):
                ui.html('<span class="panel-title">⚡ AI Scheduler Control</span>')
                is_running = state.scheduler_running
                badge_cls  = "badge-green" if is_running else "badge-red"
                badge_txt  = "RUNNING" if is_running else "STOPPED"
                ui.html(f'<span class="badge {badge_cls}">{badge_txt}</span>')

            with ui.element('div').classes('panel-body'):
                ui.html('''
                    <p style="font-family:var(--font-body);color:var(--text-muted);font-size:13px;margin-bottom:20px;line-height:1.65;">
                        The AI scheduler automatically generates and publishes social media posts.
                        Start it to enable hands-free content automation.
                    </p>
                ''')
                with ui.row().classes('gap-3'):
                    start_btn = ui.button("▶  Start Scheduler", on_click=start_scheduler).classes('btn-success')
                    stop_btn  = ui.button("■  Stop Scheduler",  on_click=stop_scheduler).classes('btn-danger')
                    start_btn.set_enabled(not state.scheduler_running)
                    stop_btn.set_enabled(state.scheduler_running)

        # ── Recent activity ──────────────────────────────────────────────────
        with ui.element('div').classes('panel'):
            with ui.element('div').classes('panel-header'):
                ui.html('<span class="panel-title">🕐 Recent Activity</span>')

            with ui.element('div').classes('panel-body'):
                with ui.element('div').classes('two-col'):

                    latest_post = AIPostService.get_latest_post()
                    with ui.element('div').classes('activity-card'):
                        ui.html('<div class="activity-title">📝 Latest Generated Post</div>')
                        if latest_post:
                            content_preview = latest_post.get('content', '')[:140]
                            ts  = latest_post.get('timestamp', 'Unknown')[:19].replace('T', ' ')
                            plat = ', '.join(latest_post.get('platforms', []))
                            ui.html(f'''
                                <div class="post-preview" style="margin-bottom:14px;">{content_preview}…</div>
                                <div class="activity-row"><span>📅</span><span>{ts}</span></div>
                                <div class="activity-row"><span>📱</span><span>{plat}</span></div>
                            ''')
                        else:
                            ui.html('<div class="activity-row" style="color:var(--text-muted);font-style:italic;">No posts generated yet.</div>')

                    with ui.element('div').classes('activity-card'):
                        ui.html('<div class="activity-title">📈 Activity Summary</div>')
                        last_p = state.last_post_time or "Never"
                        if last_p != "Never" and len(last_p) > 19:
                            last_p = last_p[:19].replace("T", " ")
                        ui.html(f'''
                            <div class="activity-row"><span>⏱</span><span>Last post: <strong style="color:var(--text-primary);">{last_p}</strong></span></div>
                            <div class="activity-row"><span>📊</span><span>Total posts: <strong style="color:var(--text-primary);">{analytics["ai_posts_generated"]}</strong></span></div>
                            <div class="activity-row"><span>📧</span><span>Emails sent: <strong style="color:var(--text-primary);">{analytics["emails_sent"]}</strong></span></div>
                            <div class="activity-row"><span>💬</span><span>WhatsApp: <strong style="color:var(--text-primary);">{analytics["whatsapp_messages"]}</strong></span></div>
                        ''')


def _stat_card(color, icon, value, label, sub, text_val=False):
    val_cls = "stat-value is-text" if text_val else "stat-value"
    with ui.element('div').classes(f'stat-card {color}'):
        with ui.element('div').classes('stat-icon-wrap'):
            ui.icon(icon).style('color:var(--accent);font-size:19px;')
        ui.html(f'<div class="{val_cls}">{value}</div>')
        ui.html(f'<div class="stat-label">{label}</div>')
        ui.html(f'<div class="stat-sub">{sub}</div>')


# ── Scheduler helpers ─────────────────────────────────────────────────────────
def start_scheduler():
    if not state.scheduler_running:
        state.scheduler_running = True
        t = threading.Thread(target=AIPostService.run_scheduler_background)
        t.daemon = True
        t.start()
        ui.notify("AI Scheduler started!", type="positive")


def stop_scheduler():
    if state.scheduler_running:
        state.scheduler_running = False
        ui.notify("AI Scheduler stopped.", type="info")


# ══════════════════════════════════════════════════════════════════════════════
#  EMAIL SENDER PAGE
# ══════════════════════════════════════════════════════════════════════════════
def email_sender_page():
    with ui.element('div').classes('page-body'):
        ui.html('''
            <div style="margin-bottom:28px;">
              <div class="section-heading">Compose Email</div>
              <div class="section-sub">Send professional emails directly from the automation hub</div>
            </div>
        ''')

        with ui.element('div').classes('panel').style('max-width:700px;'):
            with ui.element('div').classes('panel-header'):
                ui.html('<span class="panel-title">📤 New Email</span>')

            with ui.element('div').classes('panel-body'):
                recipient_email = ui.input(
                    "Recipient Email", placeholder="user@example.com"
                ).classes('w-full').style('margin-bottom:14px;')
                recipient_email.props('outlined dense')

                subject = ui.input(
                    "Subject", placeholder="What's this email about?"
                ).classes('w-full').style('margin-bottom:14px;')
                subject.props('outlined dense')

                message = ui.textarea(
                    "Message", placeholder="Write your message here…"
                ).classes('w-full').style('margin-bottom:22px;')
                message.props('outlined rows=7')

                async def send_email_handler():
                    if not recipient_email.value or not subject.value or not message.value:
                        ui.notify("Please fill in all fields!", type="negative")
                        return
                    try:
                        result = EmailService.send_email(
                            recipient_email.value, subject.value, message.value
                        )
                        if result:
                            increment_emails_sent()
                            ui.notify(f"✅ Email sent to {recipient_email.value}!", type="positive")
                            recipient_email.value = ""
                            subject.value = ""
                            message.value = ""
                        else:
                            ui.notify("❌ Failed to send email. Check logs.", type="negative")
                    except Exception as e:
                        ui.notify(f"❌ Error: {str(e)}", type="negative")

                ui.button("Send Email →", on_click=send_email_handler).classes('btn-primary')


# ══════════════════════════════════════════════════════════════════════════════
#  WHATSAPP MANAGER PAGE
# ══════════════════════════════════════════════════════════════════════════════
def whatsapp_manager_page():
    with ui.element('div').classes('page-body'):
        ui.html('''
            <div style="margin-bottom:28px;">
              <div class="section-heading">WhatsApp Manager</div>
              <div class="section-sub">Manage contacts and send WhatsApp messages at scale</div>
            </div>
        ''')

        with ui.element('div').classes('panel'):
            with ui.tabs().classes('w-full') as tabs:
                contact_tab = ui.tab('contacts', label='👥  Contacts')
                send_tab    = ui.tab('send',     label='📨  Send Message')

            with ui.tab_panels(tabs, value=contact_tab).classes('w-full'):
                with ui.tab_panel(contact_tab):
                    contact_management_section()
                with ui.tab_panel(send_tab):
                    send_message_section()


def contact_management_section():
    with ui.element('div'):
        ui.html('<div style="font-family:var(--font-display);font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:18px;letter-spacing:-0.01em;">Add New Contact</div>')

        with ui.grid(columns=2).classes('w-full gap-4').style('margin-bottom:14px;'):
            name_input  = ui.input("Full Name",    placeholder="John Doe").props('outlined dense')
            phone_input = ui.input("Phone Number", placeholder="+92 300 1234567").props('outlined dense')

        async def add_contact_handler():
            if not name_input.value or not phone_input.value:
                ui.notify("Please enter both name and phone number!", type="negative")
                return
            clean_phone = "".join(c for c in str(phone_input.value).strip() if c.isdigit() or c == "-")
            clean_name  = str(name_input.value).strip()
            contacts = load_contacts()
            if any(c["phone"] == clean_phone for c in contacts):
                ui.notify("Contact with this number already exists!", type="warning")
            else:
                contacts.append({"name": clean_name, "phone": clean_phone, "added_date": datetime.now().isoformat()})
                save_contacts(contacts)
                ui.notify(f"✅ {clean_name} added!", type="positive")
                name_input.value = ""
                phone_input.value = ""
                ui.run_javascript("location.reload();")

        ui.button("+ Add Contact", on_click=add_contact_handler).classes('btn-success').style('margin-bottom:30px;')

        contacts = load_contacts()
        if contacts:
            ui.html(f'''
                <div style="font-family:var(--font-display);font-size:15px;font-weight:700;
                            color:var(--text-primary);margin-bottom:14px;letter-spacing:-0.01em;">
                  All Contacts
                  <span style="font-family:var(--font-mono);color:var(--text-muted);
                               font-size:11px;font-weight:400;margin-left:8px;">
                    {len(contacts)} total
                  </span>
                </div>
            ''')
            for contact in contacts:
                with ui.element('div').classes('contact-card'):
                    with ui.row().classes('items-center').style('flex:1;'):
                        ui.html('<div class="contact-avatar">👤</div>')
                        with ui.column().style('gap:2px;'):
                            ui.html(f'<div class="contact-name">{contact["name"]}</div>')
                            ui.html(f'<div class="contact-meta">{contact["phone"]} · {contact["added_date"][:10]}</div>')
                    ui.button("Delete", on_click=lambda c=contact: delete_contact(c)).classes('btn-sm-danger')
        else:
            ui.html('''
                <div style="text-align:center;padding:44px;color:var(--text-muted);">
                  <div style="font-size:34px;margin-bottom:10px;">👥</div>
                  <div style="font-family:var(--font-body);font-size:13px;">No contacts yet. Add your first contact above.</div>
                </div>
            ''')


def delete_contact(contact):
    contacts = load_contacts()
    contacts.remove(contact)
    save_contacts(contacts)
    ui.notify("Contact deleted.", type="info")


def send_message_section():
    with ui.element('div'):
        ui.html('<div style="font-family:var(--font-display);font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:18px;letter-spacing:-0.01em;">Send WhatsApp Message</div>')
        contacts = load_contacts()

        if contacts:
            contact_names = [f"{c['name']}  ({c['phone']})" for c in contacts]
            contact_select = ui.select(
                options=["— Choose a contact —"] + contact_names,
                label="Select Contact",
                value="— Choose a contact —"
            ).classes('w-full').style('margin-bottom:14px;')
            contact_select.props('outlined dense')

            message_area = ui.textarea(
                "Message", placeholder="Type your WhatsApp message…"
            ).classes('w-full').style('margin-bottom:22px;')
            message_area.props('outlined rows=6')

            async def send_whatsapp_handler():
                if contact_select.value == "— Choose a contact —" or not contact_select.value:
                    ui.notify("Please select a contact!", type="negative")
                    return
                if not message_area.value.strip():
                    ui.notify("Please enter a message!", type="negative")
                    return
                selected_index = contact_names.index(contact_select.value)
                selected_phone = contacts[selected_index]["phone"]
                try:
                    result = WhatsAppService.send_message(selected_phone, message_area.value)
                    if result:
                        increment_whatsapp_sent()
                        ui.notify(f"✅ Message sent to {contact_select.value.split('(')[0].strip()}!", type="positive")
                        message_area.value = ""
                    else:
                        ui.notify("❌ Failed to send message. Check logs.", type="negative")
                except Exception as e:
                    ui.notify(f"❌ Error: {str(e)}", type="negative")

            ui.button("Send Message →", on_click=send_whatsapp_handler).classes('btn-success')
        else:
            ui.html('''
                <div style="text-align:center;padding:44px;color:var(--text-muted);">
                  <div style="font-size:34px;margin-bottom:10px;">💬</div>
                  <div style="font-family:var(--font-body);font-size:13px;">No contacts available. Add contacts in the Contacts tab first.</div>
                </div>
            ''')


# ══════════════════════════════════════════════════════════════════════════════
#  AI POST GENERATOR PAGE
# ══════════════════════════════════════════════════════════════════════════════
def ai_post_generator_page():
    with ui.element('div').classes('page-body').style('max-width:800px;'):
        ui.html('''
            <div style="margin-bottom:28px;">
              <div class="section-heading">AI Post Generator</div>
              <div class="section-sub">Automate your social media content with AI-powered scheduling</div>
            </div>
        ''')

        with ui.element('div').classes('scheduler-banner').style('margin-bottom:24px;'):
            with ui.column().style('gap:5px;flex:1;'):
                ui.html('<div style="font-family:var(--font-display);font-size:15px;font-weight:700;color:var(--text-primary);letter-spacing:-0.01em;">⚡ Automatic Posting</div>')
                ui.html('<div style="font-family:var(--font-body);font-size:12.5px;color:var(--text-muted);">When enabled, AI will generate &amp; publish content every 24 hours automatically.</div>')

            def toggle_auto_post(enabled):
                if enabled != state.scheduler_running:
                    if enabled:
                        state.scheduler_running = True
                        t = threading.Thread(target=AIPostService.run_scheduler_background)
                        t.daemon = True
                        t.start()
                        ui.notify("Auto-posting enabled!", type="positive")
                    else:
                        state.scheduler_running = False
                        ui.notify("Auto-posting disabled.", type="info")

            with ui.row().classes('items-center gap-3'):
                ui.toggle(
                    [True, False],
                    value=state.scheduler_running,
                    on_change=lambda e: toggle_auto_post(e.value),
                )
                status_lbl = "Enabled" if state.scheduler_running else "Disabled"
                color_lbl  = "var(--emerald)" if state.scheduler_running else "var(--text-muted)"
                ui.html(f'<span style="font-family:var(--font-body);font-size:13px;font-weight:600;color:{color_lbl};">{status_lbl}</span>')

        with ui.element('div').classes('panel'):
            with ui.element('div').classes('panel-header'):
                ui.html('<span class="panel-title">📄 Latest Generated Post</span>')

            with ui.element('div').classes('panel-body'):
                latest_post = AIPostService.get_latest_post()
                if latest_post:
                    content = latest_post.get('content', 'No content available')
                    ts      = latest_post.get('timestamp', 'Unknown')[:19].replace('T', ' ')
                    plat    = ', '.join(latest_post.get('platforms', []))
                    ui.html(f'''
                        <div class="post-preview" style="margin-bottom:20px;">{content}</div>
                        <div style="display:flex;gap:28px;flex-wrap:wrap;">
                          <div>
                            <div style="font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:0.12em;color:var(--text-muted);margin-bottom:5px;">Timestamp</div>
                            <div style="font-family:var(--font-mono);font-size:12px;color:var(--text-secondary);">{ts}</div>
                          </div>
                          <div>
                            <div style="font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:0.12em;color:var(--text-muted);margin-bottom:5px;">Platforms</div>
                            <div style="font-family:var(--font-body);font-size:13px;color:var(--gold);">{plat}</div>
                          </div>
                        </div>
                    ''')
                else:
                    ui.html('''
                        <div style="text-align:center;padding:44px;color:var(--text-muted);">
                          <div style="font-size:38px;margin-bottom:12px;">🤖</div>
                          <div style="font-family:var(--font-body);font-size:13.5px;">No posts generated yet. Enable auto-posting or trigger manually.</div>
                        </div>
                    ''')


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════════════
def settings_page():
    import nicegui

    with ui.element('div').classes('page-body'):
        ui.html('''
            <div style="margin-bottom:28px;">
              <div class="section-heading">Settings</div>
              <div class="section-sub">System information, statistics, and application logs</div>
            </div>
        ''')

        with ui.element('div').classes('two-col-info').style('margin-bottom:20px;'):

            with ui.element('div').classes('panel'):
                with ui.element('div').classes('panel-header'):
                    ui.html('<span class="panel-title">🖥️ System Information</span>')
                with ui.element('div').classes('panel-body'):
                    sched_color = "var(--emerald)" if state.scheduler_running else "var(--rose)"
                    sched_label = "Running" if state.scheduler_running else "Stopped"
                    ui.html(f'''
                        <div class="info-row">
                          <span class="info-key">Python Version</span>
                          <span class="info-val">{sys.version.split()[0]}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">NiceGUI Version</span>
                          <span class="info-val">{nicegui.__version__}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">Working Directory</span>
                          <span class="info-val" style="font-size:10.5px;">{os.getcwd()}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">Scheduler</span>
                          <span class="info-val" style="color:{sched_color};">{sched_label}</span>
                        </div>
                    ''')

            analytics = get_analytics_data()
            with ui.element('div').classes('panel'):
                with ui.element('div').classes('panel-header'):
                    ui.html('<span class="panel-title">📊 Application Statistics</span>')
                with ui.element('div').classes('panel-body'):
                    last_ts = (state.last_post_time or "Never")[:19].replace("T"," ") if state.last_post_time else "Never"
                    ui.html(f'''
                        <div class="info-row">
                          <span class="info-key">Emails Sent</span>
                          <span class="info-val" style="color:var(--cobalt);">{analytics["emails_sent"]}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">WhatsApp Messages</span>
                          <span class="info-val" style="color:var(--emerald);">{analytics["whatsapp_messages"]}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">AI Posts Generated</span>
                          <span class="info-val" style="color:var(--violet);">{analytics["ai_posts_generated"]}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-key">Last Post Time</span>
                          <span class="info-val">{last_ts}</span>
                        </div>
                    ''')

        with ui.element('div').classes('panel'):
            with ui.element('div').classes('panel-header'):
                ui.html('<span class="panel-title">🗒️ Application Logs</span>')
            with ui.element('div').classes('panel-body'):
                if os.path.exists("logs/app.log"):
                    with open("logs/app.log", "r") as f:
                        logs = f.read()
                    with ui.element('div').classes('log-box'):
                        log_ta = ui.textarea(value=logs).classes('w-full')
                        log_ta.props('rows=14 borderless')
                else:
                    ui.html('''
                        <div style="text-align:center;padding:32px;color:var(--text-muted);">
                          <div style="font-size:30px;margin-bottom:10px;">📋</div>
                          <div style="font-family:var(--font-body);font-size:13px;">
                            No log file found at <code style="font-family:var(--font-mono);color:var(--gold);font-size:11.5px;">logs/app.log</code>
                          </div>
                        </div>
                    ''')


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PAGE LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
@ui.page("/")
def main_page():
    ui.add_head_html(GLOBAL_CSS)

    with ui.element('div').classes('app-shell'):
        with ui.element('div').classes('sidebar'):
            sidebar_navigation()

        with ui.element('div').classes('main-content'):
            topbar()

            if state.current_page == "Dashboard":
                dashboard_page()
            elif state.current_page == "Email Sender":
                email_sender_page()
            elif state.current_page == "WhatsApp Manager":
                whatsapp_manager_page()
            elif state.current_page == "AI Post Generator":
                ai_post_generator_page()
            elif state.current_page == "Settings":
                settings_page()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="AutoPilot · Social Media AI", port=8080, reload=False)