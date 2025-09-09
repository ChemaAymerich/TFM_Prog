import React, { useEffect, useState } from 'react';

function InstagramAnalysis({ username, numPosts ,onAnalysisLoaded }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteGuide, setShowDeleteGuide] = useState(false);

  useEffect(() => {
    if (!username) return;
    setLoading(true);
    fetch('/api/instagram-analysis/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, num_posts: numPosts || 3 })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setInfo(data);
          if (onAnalysisLoaded) {
            onAnalysisLoaded(data); 
          }
        } else {
          setError(data.message || 'Error al obtener datos');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Error de conexión');
        setLoading(false);
      });
  }, [username, numPosts, onAnalysisLoaded]);

  if (loading) return <div>Cargando análisis de Instagram...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!info) return null;

  // 🔹 Función auxiliar para validar teléfonos
  const formatPhones = (phones) => {
    return phones
      ?.map((d) => (typeof d === "string" ? d : d.value))
      .filter((p) => {
        const digits = p.replace(/\D/g, "");
        return digits.length === 9 || digits.length === 11;
      })
      .join(", ") || "—";
  };

  if (showDeleteGuide) {
    return (
      <div className="ig-analysis">
        <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
          Cómo eliminar tu información de Instagram
        </h2>

        <div style={{ marginBottom: 18 }}>
          <a
            href="https://www.instagram.com/accounts/remove/request/permanent/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#3f729b", fontWeight: 600, fontSize: 16, textDecoration: "underline" }}
          >
            👉 Ir a Instagram para eliminar tu cuenta
          </a>
        </div>

        <p style={{ color: "#555", lineHeight: "1.7" }}>
          Sigue los pasos que aparecen en las capturas para eliminar o desactivar tu cuenta:
        </p>

        {[1,2,3,4,5,6].map(i => (
          <div key={i} style={{ marginBottom: 16 }}>
            <img
              src={`/img/${i}-Instagram_acceso.png`}
              alt={`Paso ${i}`}
              style={{ maxWidth: 620, borderRadius: 10, boxShadow: '0 4px 16px rgba(50,50,50,0.12)' }}
            />
          </div>
        ))}

        <button
          style={{
            background: '#bdbdbd',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: 5,
            fontWeight: 600,
            marginTop: 24,
            cursor: 'pointer'
          }}
          onClick={() => setShowDeleteGuide(false)}
        >
          ← Volver al análisis
        </button>
      </div>
    );
  }

  return (
    <div className="ig-analysis">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>

        <div>
          <h2 style={{ margin: 0, color: "#364a7c" }}>{info.full_name || username}</h2>
          <p style={{ color: '#888', margin: 0 }}>{info.bio}</p>
        </div>
      </div>

      {/* Top comentaristas */}
      <h3 style={{ color: "#6f86d6", marginBottom: 8 }}>💬 Top 10 comentaristas</h3>
      {info.top_commenters?.length > 0 ? (
        <table className="comments-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nº Comentarios</th>
            </tr>
          </thead>
          <tbody>
            {info.top_commenters.map((u) => (
              <tr key={u.username}>
                <td>{u.username}</td>
                <td>{u.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : <p style={{ color: "#777" }}>No se encontraron comentaristas</p>}

      {/* Ubicaciones */}
      <h3 style={{ color: "#6f86d6", marginTop: 20 }}>📍 Ubicaciones detectadas</h3>
      {info.locations?.length > 0 ? (
        <table className="comments-table">
          <thead>
            <tr>
              <th>Lugar</th>
              <th>Fecha de publicación</th>
            </tr>
          </thead>
          <tbody>
            {info.locations.map((lugar, idx) => (
              <tr key={idx}>
                <td>{lugar.location}</td>
                <td>{lugar.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p style={{ color: '#777' }}>No se detectaron ubicaciones</p>
      )}

      {/* Información comprometida */}
      <h3 style={{ color: "#6f86d6", marginTop: 20 }}>⚠️ Información comprometida detectada</h3>
      <ul style={{ lineHeight: "1.7", color: "#364a7c" }}>
        <li>
          <strong>DNI:</strong>{" "}
          {info.sensitive?.dnis?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>IBAN:</strong>{" "}
          {info.sensitive?.ibans?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>CCC:</strong>{" "}
          {info.sensitive?.cccs?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>Teléfonos:</strong>{" "}
          {formatPhones(info.sensitive?.phones)}
        </li>
      </ul>


      <button
        style={{
          background: '#f16b6b',
          color: 'white',
          border: 'none',
          padding: '12px 28px',
          borderRadius: 5,
          fontWeight: 600,
          cursor: 'pointer',
          fontSize: 16,
          marginTop: 20
        }}
        onClick={() => setShowDeleteGuide(true)}
      >
        Eliminar mi información de Instagram
      </button>
    </div>
  );
}

export default InstagramAnalysis;
