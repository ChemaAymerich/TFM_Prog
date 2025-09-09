import React, { useEffect, useState } from "react";

function TwitterAnalysis({ responseData }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDeleteGuide, setShowDeleteGuide] = useState(false);

  useEffect(() => {
    if (!responseData) return;
    console.log("🐦 TwitterAnalysis recibió responseData:", responseData);
    setLoading(true);

    let twitterResult = null;

    if (responseData.platform === "Twitter") {
      twitterResult = responseData;
    } else if (responseData.results && Array.isArray(responseData.results)) {
      twitterResult = responseData.results.find((r) => r.platform === "Twitter");
    }

    if (twitterResult) {
      setInfo(twitterResult);
    } else {
      setError("No se encontraron resultados de Twitter");
    }

    setLoading(false);
  }, [responseData]);

  if (loading) return <div>Cargando resultados de Twitter...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!info) return null;

  // 🔹 Función auxiliar para validar teléfonos
  const formatPhones = (phones) => {
    return phones
      ?.map((d) => (typeof d === "string" ? d : d.value))
      .filter((p) => {
        const digits = p.replace(/\D/g, "");
        return digits.length === 9 || digits.length === 11; // ej: 600123456 o +34600123456
      })
      .join(", ") || "—";
  };

  // 🔹 Vista alternativa: guía para eliminar información
  if (showDeleteGuide) {
    return (
      <div className="twitter-analysis">
        <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
          Cómo eliminar tu información de Twitter
        </h2>

        <p style={{ color: "#555", lineHeight: "1.7" }}>
          Twitter (ahora X) almacena todos tus tweets, imágenes y datos asociados a tu perfil.
          Si quieres reducir tu huella digital, puedes eliminar publicaciones o incluso desactivar tu cuenta.
        </p>

        <h3 style={{ color: "#6f86d6", marginTop: 20 }}>📌 Pasos recomendados:</h3>
        <ol style={{ lineHeight: "1.8", color: "#364a7c" }}>
          <li>Revisa y elimina manualmente los tweets que contengan información sensible.</li>
          <li>
            Para eliminar muchos tweets de golpe puedes usar herramientas externas como:{" "}
            <a
              href="https://tweetdelete.net/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#1ea7fd", fontWeight: 600 }}
            >
              TweetDelete
            </a>.
          </li>
          <li>
            Si quieres eliminar tu cuenta permanentemente, accede a:
            <br />
            <a
              href="https://help.twitter.com/es/managing-your-account/how-to-deactivate-twitter-account"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#1ea7fd", fontWeight: 600 }}
            >
              👉 Guía oficial de desactivación de cuenta
            </a>
          </li>
          <li>
            Recuerda que aunque elimines tu cuenta, copias de tus tweets pueden seguir estando en Google u
            otros sitios.
          </li>
        </ol>

        <button
          style={{
            background: "#bdbdbd",
            color: "white",
            border: "none",
            padding: "10px 20px",
            borderRadius: 5,
            fontWeight: 600,
            marginTop: 24,
            cursor: "pointer",
          }}
          onClick={() => setShowDeleteGuide(false)}
        >
          ← Volver al análisis
        </button>
      </div>
    );
  }

  const user = info.user;
  const tweets = info.tweets || [];
  const sensitive = info.sensitive || {};

  return (
    <div className="twitter-analysis">
      <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
        Resultados de búsqueda en Twitter
      </h2>

      {/* Información del usuario */}
      {user && (
        <div
          style={{
            marginBottom: 20,
            background: "#f7fafd",
            padding: "15px 20px",
            borderRadius: "8px",
            boxShadow: "0 1px 8px rgba(0,0,0,0.05)",
          }}
        >
          <h3 style={{ marginBottom: "10px", color: "#6f86d6" }}>📌 Perfil</h3>
          <p>
            <strong>Nombre:</strong> {user.name}
          </p>
          <p>
            <strong>Usuario:</strong> @{user.username}
          </p>
          <p>
            <strong>Descripción:</strong> {user.description || "—"}
          </p>
          <p>
            <strong>Creado:</strong> {new Date(user.created_at).toLocaleDateString()}
          </p>
          <p>
            <strong>Seguidores:</strong> {user.public_metrics?.followers_count}
          </p>
          <p>
            <strong>Siguiendo:</strong> {user.public_metrics?.following_count}
          </p>
          <p>
            <strong>Nº Tweets:</strong> {user.public_metrics?.tweet_count}
          </p>
        </div>
      )}

      {/* Últimos tweets */}
      <h3 style={{ marginBottom: "12px", color: "#6f86d6" }}>📝 Últimos Tweets</h3>
      {tweets.length > 0 ? (
        <table
          style={{
            width: "100%",
            borderCollapse: "separate",
            borderSpacing: 0,
            background: "#fff",
            borderRadius: "10px",
            overflow: "hidden",
            boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
            marginBottom: "24px",
          }}
        >
          <thead>
            <tr style={{ background: "#e9f4fb" }}>
              <th style={{ padding: 10 }}>Fecha</th>
              <th style={{ padding: 10 }}>Texto</th>
              <th style={{ padding: 10 }}>Likes</th>
              <th style={{ padding: 10 }}>Retweets</th>
              <th style={{ padding: 10 }}>Respuestas</th>
            </tr>
          </thead>
          <tbody>
            {tweets.map((t, i) => (
              <tr
                key={i}
                style={{ background: i % 2 ? "#fafafa" : "#fff", borderBottom: "1px solid #eee" }}
              >
                <td style={{ padding: 10, fontSize: "0.9em", color: "#627383" }}>
                  {new Date(t.created_at).toLocaleString()}
                </td>
                <td style={{ padding: 10 }}>{t.text}</td>
                <td style={{ padding: 10 }}>{t.public_metrics?.like_count}</td>
                <td style={{ padding: 10 }}>{t.public_metrics?.retweet_count}</td>
                <td style={{ padding: 10 }}>{t.public_metrics?.reply_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p style={{ color: "#888" }}>No se encontraron tweets</p>
      )}

      {/* Información comprometida */}
      <h3 style={{ marginBottom: "10px", color: "#6f86d6" }}>⚠️ Información comprometida detectada</h3>
      <ul style={{ lineHeight: "1.7", color: "#364a7c" }}>
        <li>
          <strong>DNIs:</strong>{" "}
          {sensitive.dnis?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>IBANs:</strong>{" "}
          {sensitive.ibans?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>CCCs:</strong>{" "}
          {sensitive.cccs?.map((d) => (typeof d === "string" ? d : d.value)).join(", ") || "—"}
        </li>
        <li>
          <strong>Teléfonos:</strong> {formatPhones(sensitive.phones)}
        </li>
      </ul>

      {/* Botón de eliminación */}
      <button
        style={{
          background: "#f16b6b",
          color: "white",
          border: "none",
          padding: "12px 28px",
          borderRadius: 5,
          fontWeight: 600,
          cursor: "pointer",
          fontSize: 16,
          marginTop: 20,
        }}
        onClick={() => setShowDeleteGuide(true)}
      >
        Eliminar mi información de Twitter
      </button>
    </div>
  );
}

export default TwitterAnalysis;
