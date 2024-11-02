import React, { useEffect, useState } from 'react';
import api from '../api/api'; // Your Axios instance for requests
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
                console.log('Fetching basket ID...');
                const response = await api.get('app/basket/user-basket-id', {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('token')}`,
                    },
                });
                console.log('Basket ID response:', response.data);
                const basketId = response.data.basket_id;
                setBasketId(basketId);

                console.log('Fetching basket details...');
                const basketResponse = await api.post('app/basket/', {}, {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('token')}`,
                    },
                });
                console.log('Basket details response:', basketResponse.data);
                setBasketItems(basketResponse.data.basket_items);

                const initialQuantities = {};
                basketResponse.data.basket_items.forEach(item => {
                    initialQuantities[item.id] = item.quantity;
                });
                setQuantities(initialQuantities);
            } catch (err) {
                console.error('Error fetching the basket:', err);
                setError('Error fetching the basket');
            } finally {
                setLoading(false);
            }
        };

        fetchBasket();
    }, []);

    const calculateTotalPrice = () => {
        return basketItems.reduce((total, item) => {
            const quantity = quantities[item.id] || item.quantity;
            return total + (item.product.price * quantity);
        }, 0);
    };

    if (loading) {
        return <div>Loading basket...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    if (basketItems.length === 0) {
        return <div>Your basket is empty.</div>;
    }

    const handleQuantityChange = (itemId, value) => {
        console.log('Quantity changed for item ID:', itemId, 'New value:', value);
        setQuantities({
            ...quantities,
            [itemId]: value
        });
    };

    return (
        <div>
            <h2>My Basket</h2>
            {basketItems.map((item) => (
                <div key={item.id} style={{ border: '1px solid #ddd', padding: '10px', margin: '10px 0' }}>
                    <h3>{item.product.name}</h3>
                    {item.product.product_image ? (
                        <img
                            src={`data:image/png;base64,${item.product.product_image}`}
                            alt={item.product.name}
                            style={{ width: '100px', height: '100px' }}
                        />
                    ) : (
                        <p>Image not available</p>
                    )}
                    <p>Unit Price: {item.product.price} UZS</p>
                    <p>Total Price: {quantities[item.id] * item.product.price || item.product.price} UZS</p>
                    <label>Quantity: </label>
                    <input
                        type="number"
                        min="1"
                        value={quantities[item.id] || ''}
                        onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    />
                    <button onClick={() => handleUpdateQuantity(item.id, item.product.id, basketId, quantities[item.id], item.product.price, item.quantity)}>
                        Update Quantity
                    </button>
                    <button onClick={() => handleDelete(item.id, item.quantity)}>Remove Item</button>
                </div>
            ))}
            <h3>Total Amount: {calculateTotalPrice()} UZS</h3>
            <button onClick={() => alert('Integrate a payment system')}>Pay</button>
        </div>
    );

    // Function to delete an item
    async function handleDelete(itemId, currentQuantity) {
        try {
            console.log('Deleting item with ID:', itemId);
            await api.delete(`app/basket/items/${itemId}`, {
                params: { quantity: currentQuantity },
                headers: {
                    Authorization: `Bearer ${Cookies.get('token')}`
                }
            });
            console.log('Item deleted successfully');
            setBasketItems(basketItems.filter(item => item.id !== itemId));
        } catch (error) {
            console.error('Error deleting item:', error);
            if (error.response) {
                console.error('Response data:', error.response.data);
                console.error('Response status:', error.response.status);
            }
        }
    }

    // Function to update the quantity of an item by deleting and re-adding it
    async function handleUpdateQuantity(itemId, productId, basketId, newQuantity, price, currentQuantity) {
        try {
            console.log(`Updating quantity for item ID ${itemId}: New quantity ${newQuantity}`);

            const parsedQuantity = parseInt(newQuantity, 10);
            if (isNaN(parsedQuantity) || parsedQuantity <= 0) {
                console.error('Invalid quantity value');
                return;
            }

            // Delete the current item with the total quantity to fully remove it
            console.log('Deleting current item...');
            await handleDelete(itemId, currentQuantity);

            // Prepare the request body for adding the item with the new quantity
            const requestBody = {
                product_id: productId,
                basket_id: basketId,
                quantity: parsedQuantity,
                price: price
            };
            console.log('Adding new item with updated quantity. Request body:', requestBody);

            // Add the product with the new quantity
            const addResponse = await api.post('app/basket/items', requestBody, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('token')}`
                }
            });
            console.log('Item added with new quantity:', addResponse.data);

            // Fetch updated basket to reflect changes
            const basketResponse = await api.post('app/basket/', {}, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('token')}`,
                },
            });
            setBasketItems(basketResponse.data.basket_items);
        } catch (error) {
            console.error('Error updating item quantity:', error);
            if (error.response) {
                console.error('Response data:', error.response.data);
                console.error('Response status:', error.response.status);
            }
        }
    }
};

export default BasketPage;
