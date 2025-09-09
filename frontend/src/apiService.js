// apiService.js
import axios from 'axios';

// URL base para el backend Django
const BASE_URL = 'http://localhost:8000/api/';

// Función genérica para llamadas POST
const post = async (endpoint, payload) => {
  try {
    const response = await axios.post(`${BASE_URL}${endpoint}`, payload, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error en POST ${endpoint}:`, error.response?.data || error.message);
    throw error;
  }
};

// Llama al endpoint /search/ y pasa los datos
export const searchAPI = async ({ rows, mode }) => {
  return await post("search/", { rows, mode });
};
