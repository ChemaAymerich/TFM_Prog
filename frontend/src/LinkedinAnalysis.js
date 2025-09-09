import React, { useEffect, useState } from "react";

function LinkedinAnalysis({ responseData }) {
  const [info, setInfo] = useState(null);
  const [showDeleteGuide, setShowDeleteGuide] = useState(false);

  useEffect(() => {
    if (!responseData) return;
    if (responseData.platform === "LinkedIn") {
      setInfo(responseData);
    }
  }, [responseData]);

  if (!info) return null;

  const user = info.user || {};
  const experiences = info.experiences || [];
  const educations = info.educations || [];
  const sensitive = info.sensitive || {};
  const about = info.about || "";
  const languages = info.languages || [];
  const skills = info.skills || [];

  // 🔹 Función auxiliar para validar teléfonos
  const formatPhones = (phones) => {
    return phones
      ?.map((d) => (typeof d === "string" ? d : d.value))
      .filter((p) => {
        const digits = p.replace(/\D/g, "");
        return digits.length === 9 || digits.length === 11; // 600123456 o +34600123456
      })
      .join(", ") || "—";
  };

  // 🔹 Vista alternativa: guía para eliminar info en LinkedIn
  if (showDeleteGuide) {
    return (
      <div className="linkedin-analysis" style={{ lineHeight: "1.6em" }}>
        <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
          Cómo eliminar tu información de LinkedIn
        </h2>

        <p style={{ color: "#555", lineHeight: "1.7" }}>
          LinkedIn muestra tu perfil profesional, incluyendo experiencia laboral, educación, y en muchos casos
          información personal sensible. Puedes gestionar qué información se muestra o eliminar tu cuenta si lo deseas.
        </p>

        <h3 style={{ color: "#6f86d6", marginTop: 20 }}>📌 Pasos recomendados:</h3>
        <ol style={{ lineHeight: "1.8", color: "#364a7c" }}>
          <li>
            Revisa la visibilidad de tu perfil desde la configuración:
            <br />
            <a
              href="https://www.linkedin.com/psettings/privacy"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#1ea7fd", fontWeight: 600 }}
            >
              👉 Configuración de privacidad de LinkedIn
            </a>
          </li>
          <li>
            Edita o elimina secciones específicas de tu perfil (experiencia, educación, habilidades, etc.)
            directamente desde tu perfil.
          </li>
          <li>
            Si deseas eliminar permanentemente tu cuenta:
            <br />
            <a
              href="https://www.linkedin.com/psettings/account-management/close-submit"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#1ea7fd", fontWeight: 600 }}
            >
              👉 Solicitud de cierre de cuenta
            </a>
          </li>
          <li>
            Ten en cuenta que LinkedIn puede mantener algunos datos durante un tiempo por motivos legales,
            y que información compartida públicamente puede seguir estando accesible en buscadores como Google.
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
    <div className="linkedin-analysis" style={{ lineHeight: "1.6em" }}>
      <h2 style={{ marginBottom: "20px", color: "#364a7c" }}>
        Resultados de búsqueda en LinkedIn
      </h2>

      {/* Información del usuario */}
      <div
        style={{
          marginBottom: 20,
          background: "#f7fafd",
          padding: "15px 20px",
          borderRadius: "8px",
          boxShadow: "0 1px 8px rgba(0,0,0,0.05)",
        }}
      >
        <h3 style={{ color: "#6f86d6" }}>📌 Perfil</h3>
        <p><strong>Nombre:</strong> {user.name}</p>
        <p><strong>Titular:</strong> {user.headline || "—"}</p>
        <p><strong>Ubicación:</strong> {user.location || "—"}</p>
        <p>
          <strong>Perfil:</strong>{" "}
          {user.profile_url ? (
            <a
              href={user.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#0073b1" }}
            >
              {user.profile_url}
            </a>
          ) : "—"}
        </p>
      </div>

      {/* About */}
      {about && (
        <div style={{ marginBottom: 20 }}>
          <h3 style={{ color: "#6f86d6" }}>ℹ️ Acerca de</h3>
          <p>{about}</p>
        </div>
      )}

      {/* Experiencia */}
      <h3 style={{ color: "#6f86d6" }}>💼 Experiencia</h3>
      {experiences.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {experiences.map((exp, i) => (
            <li
              key={i}
              style={{
                marginBottom: 15,
                borderLeft: "4px solid #0073b1",
                paddingLeft: 10,
              }}
            >
              <p style={{ color: "#0073b1", fontWeight: "bold" }}>
                {exp.start_date?.year} - {exp.is_current ? "Presente ✅" : exp.end_date?.year || "—"}
              </p>
              <p><strong>{exp.title}</strong> en {exp.company}</p>
              <p><em>{exp.location}</em></p>
              {exp.description && <p>{exp.description}</p>}
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: "#777" }}>No se encontró experiencia</p>
      )}

      {/* Educación */}
      <h3 style={{ color: "#6f86d6", marginTop: 20 }}>🎓 Educación</h3>
      {educations.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {educations.map((edu, i) => (
            <li
              key={i}
              style={{
                marginBottom: 15,
                borderLeft: "4px solid #0073b1",
                paddingLeft: 10,
              }}
            >
              <p style={{ color: "#0073b1", fontWeight: "bold" }}>{edu.duration}</p>
              <p><strong>{edu.school}</strong> - {edu.degree}</p>
              {edu.description && <p>{edu.description}</p>}
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: "#777" }}>No se encontró educación</p>
      )}

      {/* Idiomas */}
      {languages.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ color: "#6f86d6" }}>🌍 Idiomas</h3>
          <ul>
            {languages.map((lang, i) => (
              <li key={i}>
                {lang.language} — <em>{lang.proficiency}</em>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Habilidades */}
      {skills.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ color: "#6f86d6" }}>🛠️ Habilidades</h3>
          <ul>
            {skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Información comprometida */}
      <h3 style={{ color: "#6f86d6", marginTop: 20 }}>⚠️ Información comprometida detectada</h3>
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
        Eliminar mi información de LinkedIn
      </button>
    </div>
  );
}

export default LinkedinAnalysis;
