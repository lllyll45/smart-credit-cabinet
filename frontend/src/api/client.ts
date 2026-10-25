import axios from "axios";

const baseURL = "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});
