import React, { useEffect, useState } from 'react';
import api from '../api/api';  // Импортируем настроенный экземпляр axios

const Home = () => {
    const [products, setProducts] = useState([]);
    const [error, setError] = useState(null);
    const [quantities, setQuantities] = useState({});  // Храним количество для каждого продукта
    const [basketId, setBasketId] = useState(null);  // Храним basket_id

    useEffect(() => {
        // Получаем продукты при загрузке страницы
        const fetchProducts = async () => {
            try {
                const response = await api.get('/app/product');
                setProducts(response.data.data);  // Обновляем состояние продуктами
            } catch (error) {
                console.error('Ошибка при загрузке продуктов:', error);
                setError("Произошла ошибка при загрузке продуктов.");
            }
        };

        // Получаем basket_id для текущего пользователя
        const fetchBasketId = async () => {
            try {
                const response = await api.get('/app/basket/user-basket-id');
                setBasketId(response.data.basket_id);  // Устанавливаем basket_id
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
            [productId]: value >= 1 ? value : 1,  // Минимум 1
        }));
    };

    const handleAddToBasket = async (product) => {
        const quantity = quantities[product.id] || 1;  // Если количество не указано, по умолчанию = 1

        if (!basketId) {
            alert("Не удалось получить корзину пользователя");
            return;
        }

        try {
            await api.post('/app/basket/items', {
                product_id: product.id,
                price: product.price,  // Отправляем цену продукта
                quantity: quantity,  // Отправляем выбранное количество
                basket_id: basketId,  // Используем полученный basket_id
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
                {products.map((product, index) => (
                    <li key={index}>
                        <h3>{product.name || 'Название недоступно'}</h3>
                        <p>Цена: {product.price || 'Цена не указана'}</p>
                        <p>Описание: {product.description || 'Описание недоступно'}</p>
                        <img src={product.product_image || 'https://via.placeholder.com/150'} alt={product.name || 'Изображение недоступно'} />
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
