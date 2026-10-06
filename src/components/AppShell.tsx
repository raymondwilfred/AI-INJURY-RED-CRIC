import { useState, type ReactNode } from 'react';
import { Link, useLocation } from 'wouter';
import {
  Activity, BarChart3, ChevronDown, CircleHelp, ClipboardList, Dna,
  FileText, LayoutDashboard, Menu, Network, Search, ShieldCheck, Users, Video, X,
} from 'lucide-react';

const navigation = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/players', label: 'Players', icon: Users },
  { href: '/player-details', label: 'Player details', icon: ClipboardList },
  { href: '/structured-screening', label: 'Structured screening', icon: ShieldCheck, group: 'SCREENING' },
  { href: '/model-comparison', label: 'Model comparison', icon: BarChart3 },
  { href: '/video-analysis', label: 'Video analysis', icon: Video, group: 'MOVEMENT' },
  { href: '/system-architecture', label: 'System architecture', icon: Network },
  { href: '/methodology', label: 'Methodology', icon: FileText },
];
const pageNames: Record<string, string> = {
  '/': 'Dashboard', '/players': 'Players', '/player-details': 'Player details',
  '/structured-screening': 'Structured screening', '/model-comparison': 'Model comparison',
  '/video-analysis': 'Video analysis', '/system-architecture': 'System architecture', '/methodology': 'Methodology',
};

export function AppShell({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const page = pageNames[location] || 'Dashboard';
  return (
    <div className="app-shell flex bg-background text-foreground" data-testid="app-shell">
      {mobileOpen && <button aria-label="Close navigation" className="fixed inset-0 z-40 bg-black/60 md:hidden" onClick={() => setMobileOpen(false)} data-testid="button-close-overlay" />}
      <aside className={`sidebar fixed inset-y-0 left-0 z-50 flex w-[260px] flex-col border-r border-sidebar-border px-4 transition-transform duration-200 md:sticky md:top-0 md:h-dvh md:translate-x-0 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`} data-testid="sidebar-navigation">
        <div className="flex h-[86px] items-center justify-between border-b border-sidebar-border px-1">
          <Link href="/" className="flex items-center gap-3" data-testid="link-brand">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground"><Dna size={20} strokeWidth={2.3} /></div>
            <div><div className="font-display text-[15px] font-bold tracking-tight text-foreground">FIELDNOTE<span className="text-primary"> / AI</span></div><div className="mt-0.5 text-[10px] font-semibold uppercase tracking-[.16em] text-muted-foreground">Cricket research</div></div>
          </Link>
          <button className="rounded-lg p-2 text-muted-foreground hover:bg-sidebar-accent md:hidden" aria-label="Close menu" onClick={() => setMobileOpen(false)} data-testid="button-close-menu"><X size={17} /></button>
        </div>
        <div className="mb-3 mt-7 px-3 text-[10px] font-bold tracking-[.18em] text-muted-foreground">RESEARCH CONSOLE</div>
        <nav className="flex-1 space-y-1" aria-label="Main navigation">
          {navigation.map(({ href, label, icon: Icon, group }, index) => (
            <div key={href}>
              {group && <div className={`${index ? 'mt-6' : ''} mb-2 px-3 pt-1 text-[10px] font-bold tracking-[.17em] text-muted-foreground`}>{group}</div>}
              <Link href={href} className={`nav-link flex items-center gap-3 rounded-lg px-3 py-[10px] text-[12px] font-semibold ${location === href ? 'bg-primary/10 text-primary' : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground'}`} onClick={() => setMobileOpen(false)} data-testid={`link-nav-${href === '/' ? 'dashboard' : href.slice(1)}`}>
                <Icon size={16} strokeWidth={1.8} /><span>{label}</span>{location === href && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary status-dot" />}
              </Link>
            </div>
          ))}
        </nav>
        <div className="mb-4 rounded-xl border border-sidebar-border bg-white/[.025] p-3.5">
          <div className="mb-2 flex items-center gap-2 text-[11px] font-bold text-foreground"><span className="h-1.5 w-1.5 rounded-full bg-primary status-dot" /> Research prototype</div>
          <p className="text-[10px] leading-[1.6] text-muted-foreground">Anonymized screening and computer-vision evaluation.</p>
        </div>
        <div className="flex items-center gap-2 border-t border-sidebar-border py-4 text-[10px] text-muted-foreground"><CircleHelp size={13} /> Academic research interface <span className="ml-auto font-mono-data">v1.0</span></div>
      </aside>
      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-30 flex h-[68px] items-center justify-between border-b border-border bg-background/90 px-4 backdrop-blur-xl sm:px-7 lg:px-9">
          <div className="flex min-w-0 items-center gap-3">
            <button className="rounded-lg border border-border p-2 text-muted-foreground md:hidden" aria-label="Open navigation" onClick={() => setMobileOpen(true)} data-testid="button-open-menu"><Menu size={18} /></button>
            <div className="hidden items-center gap-2 text-[11px] text-muted-foreground sm:flex"><span>Research workspace</span><span className="text-border">/</span></div>
            <h1 className="truncate text-[13px] font-bold tracking-tight text-foreground" data-testid="text-page-title">{page}</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-[10px] text-muted-foreground sm:flex"><span className="h-1.5 w-1.5 rounded-full bg-primary status-dot" /> Dataset loaded</div>
            <div className="flex items-center gap-2 rounded-full border border-border bg-card py-1 pl-1 pr-2.5" data-testid="profile-research-workspace">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#203b33] text-[10px] font-bold text-primary">AR</span><span className="hidden text-[10px] font-semibold text-foreground sm:inline">Research team</span><ChevronDown size={12} className="text-muted-foreground" />
            </div>
          </div>
        </header>
        <main className="page-enter mx-auto w-full max-w-[1540px] px-4 py-6 sm:px-7 sm:py-8 lg:px-9" key={location}>{children}</main>
      </div>
    </div>
  );
}

export function PageIntro({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="mb-7 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.17em] text-primary"><Activity size={12} /> {eyebrow}</div><h2 className="font-display text-[27px] font-bold leading-tight tracking-[-.04em] text-foreground sm:text-[32px]" data-testid="text-page-heading">{title}</h2><p className="mt-2 max-w-2xl text-[12px] leading-6 text-muted-foreground">{description}</p></div>{action}</div>;
}

export function SearchGlyph() { return <Search size={15} />; }
