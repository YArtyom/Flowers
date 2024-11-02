import React from 'react';
import api from '../api/api';

const Logout = () => {
    const handleLogout = async () => {
        try {
            await api.post('/user/logout');
            alert('Logged out successfully!');
        } catch (error) {
            alert('Error during logout: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <button onClick={handleLogout}>Logout</button>
    );
};

export default Logout;
