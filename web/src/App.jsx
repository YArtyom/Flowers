import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import api from './api/api';  // Импортируем настроенный экземпляр axios
import Cookies from 'js-cookie';
import Home from "./components/Home.jsx";
import UserProfile from "./components/UserProfle.jsx";
import LoginForm from "./components/LoginPage.jsx";
import UpdateProfileForm from "./components/UpdateProfileForm.jsx";
import BasketPage from "./components/BasketPage.jsx";
import RegisterForm from "./components/Register.jsx";

const App = () => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkUser = async () => {
            try {
                const token = Cookies.get('token');
                if (token) {
                    // Передаем токен в заголовки
                    const response = await api.get('/user/current-user', {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    setUser(response.data);
                }
            } catch (error) {
                console.error('Ошибка при проверке пользователя:', error);
            } finally {
                setIsLoading(false);
            }
        };

        checkUser();  // Выполняем проверку пользователя при загрузке приложения
    }, []);

    const handleLogout = () => {
        Cookies.remove('token');  // Удаляем токен при выходе
        setUser(null);
    };

    if (isLoading) {
        return <div>Загрузка...</div>;
    }

    return (
        <Router>
            <nav>
                <ul>
                    <li><Link to="/">Главная</Link></li>
                    {user && <li><Link to="/profile">Профиль</Link></li>}
                    {user && <li><Link to="/basket">Корзина</Link></li>}
                    {!user && <li><Link to="/login">Вход</Link></li>}
                    {!user && <li><Link to="/register">Регистрация</Link></li>}
                    {user && <li><button onClick={handleLogout}>Выйти</button></li>}
                </ul>
            </nav>

            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/profile" element={user ? <UserProfile /> : <LoginForm />} />
                <Route path="/update-profile" element={user ? <UpdateProfileForm /> : <LoginForm />} />
                <Route path="/login" element={user ? <UserProfile /> : <LoginForm />} />
                <Route path="/register" element={user ? <UserProfile /> : <RegisterForm />} />
                <Route path="/basket" element={user ? <BasketPage /> : <LoginForm />} />
            </Routes>
        </Router>
    );
};

export default App;