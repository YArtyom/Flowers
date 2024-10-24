import React, { useEffect, useState } from 'react';
import api from '../api/api'; // Ваш экземпляр Axios для запросов
import Cookies from 'js-cookie';

const BasketPage = () => {
    const [basketItems, setBasketItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [quantities, setQuantities] = useState({});
    const [basketId, setBasketId] = useState(null);

    useEffect(() => {
        const fetchBasket = async () => {
            try {
                // Запрос для получения basket_id
                const response = await api.get('/app/basket/user-basket-id', {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('token')}`,
                    },
                });
                const basketId = response.data.basket_id;
                setBasketId(basketId);

                // Получаем детали корзины по ID
                const basketResponse = await api.get(`/app/basket/${basketId}`);
                setBasketItems(basketResponse.data.basket_items);

                // Инициализируем состояние для хранения количеств
                const initialQuantities = {};
                basketResponse.data.basket_items.forEach(item => {
                    initialQuantities[item.id] = item.quantity;
                });
                setQuantities(initialQuantities);

            } catch (err) {
                setError('Ошибка при загрузке корзины');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchBasket();
    }, []);

    if (loading) {
        return <div>Загрузка корзины...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    if (basketItems.length === 0) {
        return <div>Ваша корзина пуста.</div>;
    }

    const handleQuantityChange = (itemId, value) => {
        setQuantities({
            ...quantities,
            [itemId]: value
        });
    };

    return (
        <div>
            <h2>Моя корзина</h2>
            {basketItems.map((item) => (
                <div key={item.id} style={{ border: '1px solid #ddd', padding: '10px', margin: '10px 0' }}>
                    <h3>{item.product.name}</h3>
                    <p>Цена за единицу: {item.product.price}</p>
                    <p>Общая цена: {quantities[item.id] * item.product.price || item.product.price}</p>

                    <label>Количество: </label>
                    <input
                        type="number"
                        min="1"
                        value={quantities[item.id] || ''}
                        onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    />

                    <button onClick={() => handleUpdateQuantity(item.id, item.product.price, item.product.id, quantities[item.id], item.quantity)}>
                        Обновить количество
                    </button>
                    <button onClick={() => handleDelete(item.id, item.quantity)}>Удалить товар</button>
                </div>
            ))}
            <button onClick={() => alert('Подключите платежную систему')}>Оплатить</button>
        </div>
    );

    // Функция для удаления товара
    async function handleDelete(itemId, currentQuantity) {
        try {
            await api.delete(`/app/basket/items/${itemId}`, {
                params: { quantity: currentQuantity },  // Указываем текущее количество для полного удаления
                headers: {
                    Authorization: `Bearer ${Cookies.get('token')}`
                }
            });
            setBasketItems(basketItems.filter(item => item.id !== itemId));
        } catch (error) {
            console.error('Ошибка при удалении товара:', error);
        }
    }

    // Функция для обновления количества товара
    async function handleUpdateQuantity(itemId, price, productId, newQuantity, currentQuantity) {
        try {
            console.log(`Удаляем товар с ID ${itemId} с количеством ${currentQuantity} и добавляем с новым количеством ${newQuantity}.`);

            // Сначала удаляем существующий товар, указав текущее количество
            await api.delete(`/app/basket/items/${itemId}`, {
                params: { quantity: currentQuantity },  // Полное удаление текущего товара
                headers: {
                    Authorization: `Bearer ${Cookies.get('token')}`
                }
            });

            // Затем добавляем товар заново с новым количеством
            await api.post('/app/basket/items', {
                price: price,
                quantity: parseInt(newQuantity, 10),  // Передаём новое значение количества
                product_id: productId,
                basket_id: basketId
            });

            // Обновляем количество товара в корзине
            setBasketItems(basketItems.map(item =>
                item.id === itemId ? { ...item, quantity: parseInt(newQuantity, 10) } : item
            ));
        } catch (error) {
            console.error('Ошибка при изменении количества товара:', error);
        }
    }
};

export default BasketPage;
