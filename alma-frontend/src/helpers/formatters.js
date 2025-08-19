// src/helpers/formatters.js
export const formatDecimal = (value, decimalPlaces = 2) => {
  if (value === null || value === undefined || value === "") return "0,00";

  // Convertir a número si es string
  const number =
    typeof value === "string"
      ? parseFloat(value.replace(",", "."))
      : Number(value);

  if (isNaN(number)) return "0,00";

  // Formatear con 2 decimales fijos
  return number.toFixed(decimalPlaces).replace(".", ",");
};

export const parseDecimal = (value) => {
  if (value === null || value === undefined || value === "") return 0;

  if (typeof value === "string") {
    return parseFloat(value.replace(",", "."));
  }

  return Number(value);
};
