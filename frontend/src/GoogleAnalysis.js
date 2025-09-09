import React, { useEffect, useState } from "react";

function GoogleAnalysis({ responseData }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDeleteGuide, setShowDeleteGuide] = useState(false);

  useEffect(() => {
    if (!responseData) return;
    console.log("📡 GoogleAnalysis recibió:", responseData);

    setLoading(true);

    if (Array.isArray(responseData)) {
      setInfo(responseData);
    } else if (responseData.platform === "Google") {
      setInfo([responseData]);
    } else {
      setError("No se encontraron resultados de Google");
    }


    setLoading(false);
  }, [responseData]);

  if (loading) return <div>Cargando resultados de Google...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!info) return null;

  // 🔹 Función auxiliar para validar teléfonos
  const formatPhones = (phones) => {
    return phones
      ?.map((d) => (typeof d === "string" ? d : d.value))
      .filter((p) => {
        const digits = p.replace(/\D/g, ""); // solo números
        return digits.length === 9 || digits.length === 11; // ej: 600123456 o +34600123456
      })
      .join(", ") || "—";
  };

  // 🔹 Vista guía de eliminación
  if (showDeleteGuide) {
    return (
      <div className="google-analysis">
        <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
          Cómo solicitar la eliminación de tu información en Google
        </h2>

        <p style={{ color: "#555", lineHeight: "1.7" }}>
          Google indexa gran cantidad de información de Internet, incluyendo resultados de búsqueda,
          perfiles públicos, y en algunos casos datos personales en <strong>Google Maps</strong> o en tu
          <strong> perfil de Google</strong>. No siempre es posible eliminar todo, pero puedes solicitar la
          retirada de ciertos resultados.
        </p>

        <h3 style={{ color: "#6f86d6", marginTop: 20 }}>📌 Pasos recomendados:</h3>
        <ol style={{ lineHeight: "1.8", color: "#364a7c" }}>
          <li>
            Accede al formulario oficial de Google para retirar resultados:
            <br />
            <a
              href="https://support.google.com/websearch/troubleshooter/3111061"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#1ea7fd", fontWeight: 600 }}
            >
              👉 Solicitar retirada de contenido
            </a>
          </li>
          <li>
            Indica las URLs concretas que quieres eliminar (puedes copiarlas de la tabla de resultados).
          </li>
          <li>
            Si tu información está en tu <strong>perfil de Google</strong> o en <strong>Google Maps</strong>,
            revisa la configuración de privacidad en tu cuenta y elimina datos directamente desde allí.
          </li>
          <li>
            Ten en cuenta que aunque Google retire un resultado, la información puede seguir estando en la
            web de origen. En ese caso, deberás contactar con el administrador de la página.
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
  // 🔹 Vista principal
  return (
    <div className="google-analysis">
      <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
        Resultados de búsqueda en Google
      </h2>

      {info.map((busqueda, idx) => (
        <div key={idx} style={{ marginBottom: 40 }}>
          <h3 style={{ marginBottom: "12px", color: "#6f86d6" }}>
            🔎 Búsqueda: <span style={{ color: "#293350" }}>{busqueda.texto}</span>{" "}
            <small>({busqueda.tipo})</small>
          </h3>

          <table
            style={{
              width: "100%",
              borderCollapse: "separate",
              borderSpacing: 0,
              background: "#fff",
              borderRadius: "10px",
              overflow: "hidden",
              boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
            }}
          >
            <thead>
              <tr style={{ background: "#e9f4fb" }}>
                <th style={{ padding: 10, textAlign: "left" }}>Consulta</th>
                <th style={{ padding: 10, textAlign: "left" }}>Título</th>
                <th style={{ padding: 10, textAlign: "left" }}>URL</th>
                <th style={{ padding: 10, textAlign: "left" }}>Descripción</th>
              </tr>
            </thead>
            <tbody>
              {busqueda.results?.map((r, i) => (
                <tr
                  key={i}
                  style={{
                    background: i % 2 ? "#fafafa" : "#fff",
                    borderBottom: "1px solid #eee",
                  }}
                >
                  <td style={{ padding: 10, fontSize: "0.9em", color: "#627383" }}>{r.query}</td>
                  <td style={{ padding: 10, fontWeight: "bold", color: "#364a7c" }}>
                    {r.title || "—"}
                  </td>
                  <td style={{ padding: 10 }}>
                    {r.link ? (
                      <a
                        href={r.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "#1ea7fd", textDecoration: "none" }}
                      >
                        {r.link}
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td style={{ padding: 10, fontSize: "0.9em", color: "#444" }}>
                    {r.snippet || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Información comprometida */}
          {busqueda.sensitive && (
            <div style={{ marginTop: 20 }}>
              <h3 style={{ marginBottom: "10px", color: "#6f86d6" }}>
                ⚠️ Información comprometida detectada
              </h3>
              <ul style={{ lineHeight: "1.7", color: "#364a7c" }}>
                <li>
                  <strong>DNIs:</strong>{" "}
                  {busqueda.sensitive.dnis
                    ?.map((d) => (typeof d === "string" ? d : d.value))
                    .join(", ") || "—"}
                </li>
                <li>
                  <strong>IBANs:</strong>{" "}
                  {busqueda.sensitive.ibans
                    ?.map((d) => (typeof d === "string" ? d : d.value))
                    .join(", ") || "—"}
                </li>
                <li>
                  <strong>CCCs:</strong>{" "}
                  {busqueda.sensitive.cccs
                    ?.map((d) => (typeof d === "string" ? d : d.value))
                    .join(", ") || "—"}
                </li>
                <li>
                  <strong>Teléfonos:</strong> {formatPhones(busqueda.sensitive.phones)}
                </li>
              </ul>
            </div>
          )}
        </div>
      ))}

      {/* 🔹 Botón de eliminación */}
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
        Eliminar mi información de Google
      </button>
    </div>
  );
}

export default GoogleAnalysis;
