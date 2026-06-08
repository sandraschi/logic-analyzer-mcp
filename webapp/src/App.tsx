import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/dashboard";
import Trace from "@/pages/trace";
import Decode from "@/pages/decode";
import ToolsPage from "@/pages/tools";
import Settings from "@/pages/settings";
import Help from "@/pages/help";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trace" element={<Trace />} />
        <Route path="/decode" element={<Decode />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
