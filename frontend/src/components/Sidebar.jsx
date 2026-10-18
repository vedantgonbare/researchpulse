import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/discover", label: "Discover Papers", icon: SearchIcon },
  { to: "/dashboard", label: "My Library", icon: LibraryIcon },
  { to: "/chat", label: "Research Chat", icon: ChatIcon },
  { to: "/digest", label: "Digest", icon: DigestIcon, badge: true },
];

export function Sidebar() {
  const { logout } = useAuth();

  return (
    <nav
      aria-label="Primary"
      className="w-60 shrink-0 bg-brand-surface rounded-3xl p-5 flex flex-col gap-7 shadow-[0_2px_16px_rgba(27,37,89,0.05)]"
    >
      <div className="flex items-center gap-2.5 px-1.5">
        <div className="w-8.5 h-8.5 rounded-xl bg-brand-blue flex items-center justify-center shrink-0">
          <LogoIcon />
        </div>
        <span className="text-lg font-extrabold text-brand-navy">ResearchPulse</span>
      </div>

      <div className="flex flex-col gap-1">
        {navItems.map(({ to, label, icon: Icon, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-brand-navy text-white"
                  : "text-brand-text-muted hover:bg-brand-field"
              }`
            }
          >
            <Icon className="w-[18px] h-[18px]" />
            {label}
            {badge && (
              <span className="ml-auto bg-[#FFA451] text-white text-[11px] font-bold px-2 py-0.5 rounded-full">
                4
              </span>
            )}
          </NavLink>
        ))}
      </div>

      <button
        onClick={logout}
        className="mt-auto flex items-center gap-2.5 p-3 rounded-2xl bg-brand-field text-left"
      >
        <div className="w-8 h-8 rounded-full bg-brand-blue text-white text-[13px] font-bold flex items-center justify-center shrink-0">
          VG
        </div>
        <div className="min-w-0">
          <div className="text-[13px] font-bold text-brand-navy truncate">Vedant Gonbare</div>
          <div className="text-xs text-brand-text-faint">Log out</div>
        </div>
      </button>
    </nav>
  );
}

function LogoIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="1.8" />
      <path d="M12 8v4l2.5 1.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function SearchIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
      <path d="M21 21l-4.3-4.3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function LibraryIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 19.5V5.5A1.5 1.5 0 0 1 5.5 4H17a1 1 0 0 1 1 1v15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 4v15M4 19.5A1.5 1.5 0 0 0 5.5 21H18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function ChatIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 4h12l4 4v12H4z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M8 11h8M8 15h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function DigestIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="4" y="5" width="16" height="15" rx="2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M4 9.5h16M8 3v3M16 3v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}