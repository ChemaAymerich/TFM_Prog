// Dashboard.js
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './Dashboard.css';
import InstagramAnalysis from './InstagramAnalysis';
import GoogleAnalysis from './GoogleAnalysis';
import TwitterAnalysis from './TwitterAnalysis';
import LinkedinAnalysis from './LinkedinAnalysis';

const SIDEBAR_ITEMS = [
  { key: 'resumen', label: 'Resumen', icon: '📊' },
  { key: 'instagram', label: 'Instagram', icon: '📸' },
  { key: 'twitter', label: 'Twitter', icon: '✖️' },
  { key: 'linkedin', label: 'LinkedIn', icon: '🔗' },
  { key: 'google', label: 'Google', icon: '🌐' },
];

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const rawResponse = location.state?.responseData || [];

  console.log("🌍 responseData bruto recibido en Dashboard:", rawResponse);

  const responseData = Array.isArray(rawResponse) ? rawResponse : [rawResponse];
  const [activeTab, setActiveTab] = useState('resumen');
  const [fileLink, setFileLink] = useState('');
  const [instaAnalysis, setInstaAnalysis] = useState(null);
  const photoCount = 3;

  const instaData = responseData.find(r => r.platform === "Instagram");
  const twitterData = responseData.find(r => r.platform === "Twitter");
  const linkedinData = responseData.find(r => r.platform === "LinkedIn");
  const googleData = responseData.filter(r => r.platform === "Google"); // array siempre
  console.log("🌐 GoogleData en Dashboard:", googleData);
  const username = instaData?.username;

  useEffect(() => {
    if (activeTab === 'instagram' && instaData?.status === 'success') {
      extractPosts(photoCount);
    }
  }, [activeTab, responseData]);

  const extractPosts = async (photoCount) => {
    try {
      const res = await fetch('/extract_posts/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, num_posts: photoCount })
      });
      const data = await res.json();
      if (data.status === 'success' || data.status === 'skipped') {
        setFileLink(`/media/${username}/${photoCount}/user_posts.json`);
      }
    } catch (error) {
      setFileLink('');
    }
  };

  const extractValues = (arr = []) => {
    return arr.map(item =>
      typeof item === "string" ? item : item?.value
    ).filter(Boolean);
  };

  const formatPhones = (phones = []) => {
    return extractValues(phones).filter(p =>
      /^\+?\d{9,15}$/.test(p)
    );
  };

  // 🔹 Render resumen
  const renderResumen = () => {
    const centralName =
      linkedinData?.user?.name ||
      (googleData[0]?.texto || googleData[0]?.results?.[0]?.title) ||
      instaData?.username ||
      twitterData?.user?.username ||
      "Usuario";

    const instaLocations = instaData?.locations?.map(l => l.location) || [];
    const linkedinLocations = linkedinData?.user?.location
      ? [linkedinData.user.location]
      : [];
    const allLocations = [...instaLocations, ...linkedinLocations];

    // Fusionar sensibles de todas las plataformas
    const allDnis = extractValues([
      ...(googleData.flatMap(g => g?.sensitive?.dnis || [])),
      ...(linkedinData?.sensitive?.dnis || []),
      ...(twitterData?.sensitive?.dnis || []),
      ...(instaData?.sensitive?.dnis || []),
      ...(instaAnalysis?.sensitive?.dnis || []),
    ]);

    const allIbans = extractValues([
      ...(googleData.flatMap(g => g?.sensitive?.ibans || [])),
      ...(linkedinData?.sensitive?.ibans || []),
      ...(twitterData?.sensitive?.ibans || []),
      ...(instaData?.sensitive?.ibans || []),
      ...(instaAnalysis?.sensitive?.ibans || []),
    ]);

    const allPhones = formatPhones([
      ...(googleData.flatMap(g => g?.sensitive?.phones || [])),
      ...(linkedinData?.sensitive?.phones || []),
      ...(twitterData?.sensitive?.phones || []),
      ...(instaData?.sensitive?.phones || []),
      ...(instaAnalysis?.sensitive?.phones || []),
    ]);

    console.log("📊 Datos Google en resumen:", googleData);

    const highlights = [
      {
        key: 'instagram',
        label: 'Instagram',
        icon: '📸',
        content: (
          <p><strong>Bio:</strong> {instaData?.user_data?.data?.user?.biography || "—"}</p>
        ),
      },
      {
        key: 'twitter',
        label: 'Twitter',
        icon: '✖️',
        content: twitterData?.user ? (
          <ul>
            <li><strong>Nombre:</strong> {twitterData.user.name}</li>
            <li><strong>Usuario:</strong> @{twitterData.user.username}</li>
            <li><strong>Descripción:</strong> {twitterData.user.description || "—"}</li>
            <li><strong>Creado:</strong> {new Date(twitterData.user.created_at).toLocaleDateString()}</li>
            <li><strong>Seguidores:</strong> {twitterData.user.public_metrics?.followers_count}</li>
            <li><strong>Siguiendo:</strong> {twitterData.user.public_metrics?.following_count}</li>
            <li><strong>Nº Tweets:</strong> {twitterData.user.public_metrics?.tweet_count}</li>            
          </ul>
        ) : <p>Sin datos</p>,
      },
      {
        key: 'linkedin',
        label: 'LinkedIn',
        icon: '🔗',
        content: (

          <>
            <p>{linkedinData?.user?.headline || "Sin datos"}</p>
            <p>{linkedinData?.user?.location || ""}</p>
            <p><strong>Trabajo:</strong> {linkedinData?.experiences?.[0]?.title || "—"}</p>
          </>
        ),
      },
      {
        key: 'google',
        label: 'Google',
        icon: '🌐',
        content: googleData.length > 0 && googleData[0]?.results?.length > 0 ? (
          <ul style={{ paddingLeft: 16 }}>
            {googleData[0].results.slice(0, 3).map((r, i) => (
              <li key={i} style={{ marginBottom: 6 }}>
                <strong>{r.title || "—"}</strong><br />
                <a href={r.link} target="_blank" rel="noreferrer" style={{ color: "#1ea7fd" }}>
                  {r.link}
                </a>
              </li>
            ))}
          </ul>
        ) : <p>Sin datos</p>,
      },
      {
        key: 'sensitive',
        label: 'Información comprometida detectada',
        icon: '⚠️',
        content: (
          <ul>
            <li><strong>DNI:</strong> {allDnis.length > 0 ? allDnis.join(", ") : "—"}</li>
            <li><strong>IBAN:</strong> {allIbans.length > 0 ? allIbans.join(", ") : "—"}</li>
            <li><strong>Teléfonos:</strong> {allPhones.length > 0 ? allPhones.join(", ") : "—"}</li>
          </ul>
        ),
      },
      {
        key: 'locations',
        label: 'Ubicaciones',
        icon: '📍',
        content: allLocations.length > 0 ? (
          <ul>
            {allLocations.slice(0, 4).map((loc, i) => (
              <li key={i}>{loc}</li>
            ))}
            {allLocations.length > 4 && (
              <li>+{allLocations.length - 4} más...</li>
            )}
          </ul>
        ) : <p>—</p>,
      },
    ];

    return (
      <div className="resumen-container">
        <h2 style={{ marginBottom: 30 }}>Resumen general</h2>
        <div className="circle-container">
          <div className="central-circle">{centralName}</div>
          {highlights.map((h, idx) => (
            <div key={idx} className={`circle-item circle-${idx}`}>
              <div style={{ fontSize: "1.3em" }}>{h.icon}</div>
              <strong>{h.label}</strong>
              <div className="circle-content">{h.content}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'resumen':
        return renderResumen();
      case 'instagram':
        return instaData ? (
          <InstagramAnalysis
            username={instaData.username}
            numPosts={photoCount}
            onAnalysisLoaded={setInstaAnalysis}
          />
        ) : <div>No hay datos de Instagram</div>;
      case 'google':
        console.log("🟦 Renderizando Google con bloques:", googleData);
        return googleData.length > 0 ? (
          <GoogleAnalysis responseData={googleData} />
        ) : <div>No hay datos de Google</div>;
      case 'twitter':
        return twitterData ? (
          <TwitterAnalysis responseData={twitterData} />
        ) : <div>No hay datos de Twitter</div>;
      case 'linkedin':
        return linkedinData ? (
          <LinkedinAnalysis responseData={linkedinData} />
        ) : <div>No hay datos de LinkedIn</div>;
      default:
        return <div>En futuras versiones...</div>;
    }
  };

  return (
    <div className="dashboard-root">
      <aside className="dashboard-sidebar">
        <div className="sidebar-title">
          <strong>Gestión de Identidad</strong>
        </div>
        {SIDEBAR_ITEMS.map(item => (
          <button
            key={item.key}
            className={`sidebar-btn ${activeTab === item.key ? 'active' : ''}`}
            onClick={() => setActiveTab(item.key)}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
        <button
          className="sidebar-btn back"
          onClick={() => navigate('/')}
          style={{ marginTop: 'auto' }}
        >
          ⬅️ Volver al inicio
        </button>
      </aside>
      <main className="dashboard-content">
        {renderContent()}
      </main>
    </div>
  );
}

export default Dashboard;
