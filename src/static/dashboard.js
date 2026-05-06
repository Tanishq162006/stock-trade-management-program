const chartData = window.stockTradeData || {};

const rupeeFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2
});

function emptyChart(canvasId, message) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const parent = canvas.parentElement;
  const emptyState = document.createElement("p");
  emptyState.className = "empty-chart";
  emptyState.textContent = message;
  parent.replaceChildren(emptyState);
}

function renderIndustryChart() {
  if (!chartData.industry_labels?.length) {
    emptyChart("industryChart", "Add profitable trades to see industry share.");
    return;
  }

  new Chart(document.getElementById("industryChart"), {
    type: "doughnut",
    data: {
      labels: chartData.industry_labels,
      datasets: [{
        data: chartData.industry_values,
        backgroundColor: ["#2563eb", "#16a34a", "#eab308", "#dc2626", "#7c3aed", "#0891b2"],
        borderColor: "#ffffff",
        borderWidth: 2
      }]
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: context => `${context.label}: ${rupeeFormatter.format(context.parsed)}`
          }
        }
      }
    }
  });
}

function renderMonthlyChart() {
  if (!chartData.month_labels?.length) {
    emptyChart("monthlyChart", "Add trades to see monthly performance.");
    return;
  }

  new Chart(document.getElementById("monthlyChart"), {
    type: "bar",
    data: {
      labels: chartData.month_labels,
      datasets: [{
        label: "Profit/Loss",
        data: chartData.month_values,
        backgroundColor: chartData.month_values.map(value => value >= 0 ? "#16a34a" : "#dc2626"),
        borderRadius: 4
      }]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { callback: value => rupeeFormatter.format(value) }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => rupeeFormatter.format(context.parsed.y)
          }
        }
      }
    }
  });
}

function renderForecastChart() {
  if (!chartData.forecast_labels?.length) {
    emptyChart("forecastChart", "Add repeated trades for a ticker to see a forecast.");
    return;
  }

  const historyLength = chartData.forecast_history.length;
  const forecastHistoryPadding = Array(chartData.forecast_values.length - historyLength).fill(null);

  new Chart(document.getElementById("forecastChart"), {
    type: "line",
    data: {
      labels: chartData.forecast_labels,
      datasets: [
        {
          label: "Recorded Price",
          data: chartData.forecast_history.concat(forecastHistoryPadding),
          borderColor: "#2563eb",
          backgroundColor: "#2563eb",
          tension: 0.25
        },
        {
          label: "Forecast",
          data: chartData.forecast_values,
          borderColor: "#c48a00",
          backgroundColor: "#c48a00",
          borderDash: [5, 5],
          tension: 0.25
        }
      ]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { callback: value => rupeeFormatter.format(value) }
        }
      }
    }
  });
}

renderIndustryChart();
renderMonthlyChart();
renderForecastChart();
