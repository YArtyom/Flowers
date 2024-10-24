import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie'; // Импортируем библиотеку для работы с куки

const UserProfile = () => {
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getCurrentUser = async () => {
            try {
                const token = Cookies.get('token');
                if (!token) {
                    setError('Токен не найден в куки. Пожалуйста, войдите в систему.');
                    return;
                }

                const response = await axios.get('http://127.0.0.1:9000/user/current-user', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setUser(response.data);  // Сохраняем данные пользователя
            } catch (error) {
                console.error('Ошибка:', error);
                setError("Произошла ошибка при получении профиля.");
            }
        };

        getCurrentUser();
    }, []);

    if (error) {
        return <div>{error}</div>;
    }

    if (!user) {
        return <div>Загрузка профиля...</div>;
    }

    return (
        <div>
            <h2>Мой профиль</h2>
            <p>Имя: {user.name}</p>
            <p>Email: {user.email}</p>
            <button onClick={() => window.location.href='/update-profile'}>Обновить профиль</button>
        </div>
    );
};

export default UserProfile;
