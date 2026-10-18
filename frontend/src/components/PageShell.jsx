import { Sidebar } from "./Sidebar";

export function PageShell({ children }) {
  return (
    <div className="flex flex-wrap min-h-screen w-full box-border p-5 gap-5">
      <Sidebar />
      <main className="flex-[999_1_720px] min-w-0 flex flex-col gap-5">
        {children}
      </main>
    </div>
  );
}