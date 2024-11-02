import axios from 'axios';
import Cookies from 'js-cookie';

// Создаем экземпляр Axios
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',  // URL вашего API
});

// Добавляем перехватчик запросов для автоматического добавления токена
api.interceptors.request.use(
    (config) => {
        const token = Cookies.get('token');  // Извлекаем токен из куки
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;  // Добавляем токен в заголовок Authorization
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
