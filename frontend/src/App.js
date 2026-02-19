import React, { useEffect, useMemo, useState } from "react";
import { Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import ComposePage from "./pages/ComposePage";
import ConnectionsPage from "./pages/ConnectionsPage";
import HistoryPage from "./pages/HistoryPage";
import AutomationPage from "./pages/AutomationPage";
import { getAuthStatus, getAuthorizeUrl, sendPost } from "./api";

export default function App() {
  const [content, setContent] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [platforms, setPlatforms] = useState({
    facebook: true,
    instagram: false,
    twitter: false,
  });

  const [connected, setConnected] = useState({
    facebook: false,
    instagram: false,
    twitter: false,
    linkedin: false,
  });
  const [connectLoading, setConnectLoading] = useState(false);
  const [connectError, setConnectError] = useState(null);

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const userId = "demo-user-1";

  const refreshAuthStatus = async () => {
    try {
      const data = await getAuthStatus(userId);
      setConnected(data.connected || { facebook: false, instagram: false, twitter: false, linkedin: false });
    } catch (e) {
      setConnected({ facebook: false, instagram: false, twitter: false, linkedin: false });
    }
  };

  const onConnect = async (platform) => {
    setConnectError(null);
    setConnectLoading(true);
    try {
      const url = await getAuthorizeUrl(platform, userId);
      if (!url) throw new Error("Missing authorize_url");
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (e) {
      setConnectError(e?.response?.data || e.message);
    } finally {
      setConnectLoading(false);
    }
  };

  useEffect(() => {
    refreshAuthStatus();
  }, []);

  const selectedPlatforms = useMemo(() => {
    return Object.entries(platforms)
      .filter(([, v]) => v)
      .map(([k]) => k);
  }, [platforms]);

  const togglePlatform = (key) => {
    setPlatforms((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();

    if (!content.trim()) return;
    if (selectedPlatforms.length === 0) return;

    setLoading(true);
    try {
      const res = await sendPost({
        userId,
        content,
        platforms: selectedPlatforms,
        imageFile,
      });

      const item = {
        id: res.request_id,
        ts: new Date().toISOString(),
        content,
        platforms: selectedPlatforms,
        results: res.results,
      };

      setHistory((prev) => [item, ...prev]);
      setContent("");
      setImageFile(null);
      refreshAuthStatus();
    } catch (err) {
      const item = {
        id: `local-${Date.now()}`,
        ts: new Date().toISOString(),
        content,
        platforms: selectedPlatforms,
        results: [
          {
            platform: "request",
            status: "failed",
            error: err?.response?.data || err.message,
          },
        ],
      };
      setHistory((prev) => [item, ...prev]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout connected={connected}>
      <Routes>
        <Route path="/" element={<DashboardPage connected={connected} history={history} />} />
        <Route
          path="/compose"
          element={
            <ComposePage
              content={content}
              setContent={setContent}
              imageFile={imageFile}
              setImageFile={setImageFile}
              platforms={platforms}
              togglePlatform={togglePlatform}
              loading={loading}
              onSubmit={onSubmit}
              connected={connected}
            />
          }
        />
        <Route
          path="/connections"
          element={
            <ConnectionsPage
              userId={userId}
              connected={connected}
              connectLoading={connectLoading}
              connectError={connectError}
              onConnect={onConnect}
              onRefresh={refreshAuthStatus}
            />
          }
        />
        <Route path="/automation" element={<AutomationPage userId={userId} />} />
        <Route path="/history" element={<HistoryPage history={history} />} />
      </Routes>
    </AppLayout>
  );
}
