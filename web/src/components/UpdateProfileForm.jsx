import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';  // Для навигации

const UpdateProfileForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [showPassword, setShowPassword] = useState(false);  // Управляем видимостью пароля
    const [error, setError] = useState(null);
    const [userId, setUserId] = useState(null);  // Состояние для хранения ID пользователя
    const navigate = useNavigate();  // Для навигации

    useEffect(() => {
        const getCurrentUser = async () => {
            try {
                const token = Cookies.get('token');
                if (!token) {
                    setError('Токен не найден в куки. Пожалуйста, войдите в систему.');
                    return;
                }

                const response = await axios.get('http://127.0.0.1:8000/user/current-user', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                // Заполняем форму данными профиля
                setFormData({
                    name: response.data.name,
                    email: response.data.email,
                    password: '',  // Пароль не заполняем
                    confirmPassword: '',  // Подтверждение пароля
                });

                // Сохраняем ID пользователя
                setUserId(response.data.id);
            } catch (error) {
                console.error('Ошибка при загрузке профиля:', error);
                setError("Произошла ошибка при загрузке профиля.");
            }
        };

        getCurrentUser();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            setError('Пароли не совпадают');
            return;
        }

        try {
            const token = Cookies.get('token');
            if (!token) {
                setError('Токен не найден. Пожалуйста, войдите в систему.');
                return;
            }

            // Подготавливаем данные для отправки (исключаем незаполненные поля)
            const dataToSend = {};
            if (formData.name) dataToSend.name = formData.name;
            if (formData.email) dataToSend.email = formData.email;
            if (formData.password) dataToSend.password = formData.password; // Если есть новый пароль, отправляем его

            // Обновляем профиль по ID пользователя
            await axios.put(`http://127.0.0.1:8000/user/update_user/${userId}`, dataToSend, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            alert('Профиль успешно обновлен!');
            navigate('/profile');  // Возвращаемся на страницу профиля
        } catch (error) {
            console.error('Ошибка при обновлении профиля:', error);
            setError("Ошибка при обновлении профиля: " + (error.response?.data?.detail || error.message));
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const toggleShowPassword = () => {
        setShowPassword(!showPassword);  // Переключаем видимость пароля
    };

    return (
        <div>
            <h2>Обновление профиля</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Имя:
                    <input type="text" name="name" value={formData.name} onChange={handleChange} />
                </label>
                <br />
                <label>
                    Email:
                    <input type="email" name="email" value={formData.email} onChange={handleChange} />
                </label>
                <br />
                <label>
                    Пароль:
                    <input
                        type={showPassword ? "text" : "password"}
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <button type="button" onClick={toggleShowPassword}>
                        {showPassword ? 'Скрыть пароль' : 'Показать пароль'}
                    </button>
                </label>
                <br />
                <label>
                    Подтверждение пароля:
                    <input
                        type={showPassword ? "text" : "password"}
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                    />
                </label>
                <br />
                <button type="submit">Обновить профиль</button>
            </form>
            {error && <p>{error}</p>}
        </div>
    );
};

export default UpdateProfileForm;
