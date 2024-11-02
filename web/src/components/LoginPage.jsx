import React, { useState } from 'react';
import api from '../api/api';
import Cookies from 'js-cookie';  // Импортируем библиотеку для работы с куки

const LoginForm = ({ onLogin }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Отправляем запрос на сервер с username, email и password
            const response = await api.post('/user/login', formData);

            // Сохраняем токен в куки
            Cookies.set('token', response.data.auth_token, { expires: 1 }); // Токен будет храниться 1 день

            // Также можем сохранить токен в localStorage (если это требуется)
            localStorage.setItem('access_token', response.data.auth_token);

            alert('Login successful!');

            // Вызываем callback чтобы обновить состояние приложения (например, скрыть ссылки)
            if (onLogin) {
                onLogin();
            }

        } catch (error) {
            alert('Ошибка при входе: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Вход</h2>
            <label>
                Username:
                <input type="text" name="username" value={formData.username} onChange={handleChange} required />
            </label>
            <br />
            <label>
                Email:
                <input type="email" name="email" value={formData.email} onChange={handleChange} required />
            </label>
            <br />
            <label>
                Password:
                <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </label>
            <br />
            <button type="submit">Войти</button>
        </form>
    );
};

export default LoginForm;
