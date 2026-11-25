
export function unwrapResponse(response) {
  let value = response?.data ?? response;

  // Support the project's { success, message, data } response format.
  if (value && typeof value === "object" && "data" in value) {
    value = value.data;
  }

  return value;
}

export function extractList(value) {
  if (Array.isArray(value)) return value;

  if (!value || typeof value !== "object") return [];

  if (Array.isArray(value.results)) return value.results;
  if (Array.isArray(value.items)) return value.items;
  if (Array.isArray(value.data)) return value.data;

  return [];
}

export function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(Number(value) || 0);
}

export function formatPercentage(value) {
  const number = Number(value) || 0;
  return `${number.toFixed(1)}%`;
}

export function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function humanize(value) {
  if (!value) return "Unknown";

  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
