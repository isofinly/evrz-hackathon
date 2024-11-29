import React, { useState } from "react";
import axios from "axios";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  url?: string;
}

const Button: React.FC<ButtonProps> = ({ children, onClick, url }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (url) {
      setLoading(true);
      try {
        const response = await axios.get(url);
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    }
    onClick && onClick();
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? "Loading..." : children}
    </button>
  );
};

export default Button;
