import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';  // Импортируем настроенный экземпляр axios
import Cookies from 'js-cookie';

const Home = () => {
    const [products, setProducts] = useState([]);
    const [error, setError] = useState(null);
    const [quantities, setQuantities] = useState({});
    const [images, setImages] = useState({}); // Храним изображения для каждого продукта
    const [basketId, setBasketId] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        // Получаем продукты при загрузке страницы
        const fetchProducts = async () => {
            try {
                const response = await api.get('/app/product');
                setProducts(response.data.data);  // Обновляем состояние продуктами

                // Для каждого продукта делаем запрос на изображение
                response.data.data.forEach((product) => fetchProductImage(product.id));
            } catch (error) {
                console.error('Ошибка при загрузке продуктов:', error);
                setError("Произошла ошибка при загрузке продуктов.");
            }
        };

        // Функция для получения изображения продукта по ID
        const fetchProductImage = async (productId) => {
            try {
                const response = await api.get(`/app/product/${productId}/image`, {
                    responseType: 'blob' // Ожидаем бинарный формат для изображения
                });
                // Создаем URL для изображения и обновляем состояние
                const imageUrl = URL.createObjectURL(response.data);
                setImages((prevImages) => ({ ...prevImages, [productId]: imageUrl }));
            } catch (error) {
                console.error(`Ошибка при загрузке изображения для продукта с ID ${productId}:`, error);
            }
        };

        // Получаем basket_id для текущего пользователя
        const fetchBasketId = async () => {
            try {
                const token = Cookies.get('token');
                if (!token) {
                    return;
                }
                const response = await api.get('/app/basket/user-basket-id', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setBasketId(response.data.basket_id);
            } catch (error) {
                console.error('Ошибка при получении basket_id:', error);
            }
        };

        fetchProducts();  // Загружаем продукты
        fetchBasketId();  // Загружаем basket_id
    }, []);

    const handleQuantityChange = (productId, value) => {
        setQuantities((prevQuantities) => ({
            ...prevQuantities,
            [productId]: value >= 1 ? value : 1,
        }));
    };

    const handleAddToBasket = async (product) => {
        const token = Cookies.get('token');
        if (!token) {
            alert("Пожалуйста, войдите в систему, чтобы добавить товары в корзину.");
            navigate('/login');
            return;
        }

        const quantity = quantities[product.id] || 1;

        if (!basketId) {
            alert("Не удалось получить корзину пользователя");
            return;
        }

        try {
            await api.post('/app/basket/items', {
                product_id: product.id,
                price: product.price,
                quantity: quantity,
                basket_id: basketId,
            });

            alert('Товар добавлен в корзину!');
        } catch (error) {
            console.error('Ошибка при добавлении товара в корзину:', error);
            alert("Произошла ошибка при добавлении товара в корзину.");
        }
    };

    if (error) {
        return <div>{error}</div>;
    }

    if (!products.length) {
        return <div>Загрузка продуктов...</div>;
    }

    return (
        <div>
            <h2>Наши продукты</h2>
            <ul>
                {products.map((product) => (
                    <li key={product.id}>
                        <h3>{product.name || 'Название недоступно'}</h3>
                        <p>Цена: {product.price || 'Цена не указана'} UZS</p>
                        <p>Описание: {product.description || 'Описание недоступно'}</p>
                        <img
                            src={images[product.id] || 'https://via.placeholder.com/150'}
                            alt={product.name || 'Изображение недоступно'}
                        />
                        <label>
                            Количество:
                            <input
                                type="number"
                                min="1"
                                value={quantities[product.id] || 1}
                                onChange={(e) => handleQuantityChange(product.id, parseInt(e.target.value))}
                            />
                        </label>
                        <button onClick={() => handleAddToBasket(product)}>Добавить в корзину</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Home;
