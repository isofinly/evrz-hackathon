import React, { useState } from "react";

const BadComponent = () => {
  const [count, setCount] = useState(0);

  const handleComplexCalculation = (value: number) => {
    let result = 0;
    for (let i = 0; i < value; i++) {
      result += Math.pow(i, 2);
    }
    return result;
  };

  const processData = (data: any[]) => {
    const filtered = data.filter((item) => item.active);
    const mapped = filtered.map((item) => {
      return {
        ...item,
        processed: true,
        timestamp: Date.now(),
      };
    });
    return mapped;
  };

  const formatUserName = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0).toUpperCase()}${firstName.slice(
      1
    )} ${lastName.toUpperCase()}`;
  };

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
    </div>
  );
};
