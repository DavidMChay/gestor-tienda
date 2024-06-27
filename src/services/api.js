// src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Ajusta la URL según sea necesario

export const getProducts = async () => {
  try {
    const response = await axios.get(`${API_URL}/products`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

export const addProduct = async (product) => {
  try {
    const response = await axios.post(`${API_URL}/products`, product);
    return response.data.data;
  } catch (error) {
    console.error('Error adding product:', error);
    throw error;
  }
};

// Otros servicios según sea necesario...
