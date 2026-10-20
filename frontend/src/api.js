import axios from 'axios';

//const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// NEW (Replace with your actual ngrok URL)
//const BASE_URL = 'https://prowling-frayed-fax.ngrok-free.dev';

const BASE_URL = 'https://aquaflow-portal.onrender.com/';

const api = axios.create({
    baseURL: BASE_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});


api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

/*
api.interceptors.request.use((config) => {
    // THIS IS THE MAGIC LINE TO BYPASS NGROK WARNING
    config.headers['ngrok-skip-browser-warning'] = 'true';

    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
*/

export default api;
