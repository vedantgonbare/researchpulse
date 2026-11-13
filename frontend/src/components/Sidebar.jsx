import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect } from "react";
import { apiRequest } from "../api/client";
import {
  Search as SearchIcon,
  Library as LibraryIcon,
  MessageCircle as ChatIcon,
  BookOpen as DigestIcon,
  Activity as LogoIcon,
} from "lucide-react";

const studentNavItems = [
  { to: "/discover", label: "Discover Papers", icon: SearchIcon },
  { to: "/dashboard", label: "My Library", icon: LibraryIcon },
  { to: "/chat", label: "Research Chat", icon: ChatIcon },
  { to: "/digest", label: "Digest", icon: DigestIcon, badge: true },
];

const professorNavItems = [
  { to: "/professor/dashboard", label: "My Students", icon: LibraryIcon },
  { to: "/professor/assignments", label: "Assignments", icon: ChatIcon },
];

export function Sidebar() {
  const { logout, token, user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(null);

  const navItems = user?.role === "professor" ? professorNavItems : studentNavItems;

  useEffect(() => {
    // The digest badge is a student-only concept — don't fire this
    // request at all for a professor, there's nothing for it to show.
    if (user?.role !== "student") return;

    let cancelled = false;
    apiRequest("/papers/digest", { token })
      .then((data) => {
        if (!cancelled) setUnreadCount(data.total_unread);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [token, user]);

  const initials = user?.username
    ? user.username.slice(0, 2).toUpperCase()
    : "..";

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
            <Icon className="w-4.5 h-4.5" />
            {label}
            {badge && unreadCount !== null && unreadCount > 0 && (
              <span className="ml-auto bg-[#FFA451] text-white text-[11px] font-bold px-2 py-0.5 rounded-full">
                {unreadCount}
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
          {initials}
        </div>
        <div className="min-w-0">
          <div className="text-[13px] font-bold text-brand-navy truncate">
            {user?.username ?? "..."}
          </div>
          <div className="text-xs text-brand-text-faint">Log out</div>
        </div>
      </button>
    </nav>
  );
}

// ...icon functions unchanged, keep them exactly as they are