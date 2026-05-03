const chartData = window.stockTradeData || {
  industryLabels: [],
  industryValues: [],
  monthLabels: [],
  monthValues: []
};

const rupeeFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2
});

function emptyChart(canvasId, message) {
  const canvas = document.getElementById(canvasId);
  const parent = canvas.parentElement;
  const emptyState = document.createElement("p");
  emptyState.className = "empty-chart";
  emptyState.textContent = message;
  parent.replaceChildren(emptyState);
}

function renderIndustryChart() {
  if (!chartData.industryLabels.length) {
    emptyChart("industryChart", "Add trades to see industry profit/loss.");
    return;
  }

  new Chart(document.getElementById("industryChart"), {
    type: "doughnut",
    data: {
      labels: chartData.industryLabels,
      datasets: [{
        data: chartData.industryValues,
        backgroundColor: ["#2563eb", "#16a34a", "#eab308", "#dc2626", "#7c3aed", "#0891b2"],
        borderColor: "#ffffff",
        borderWidth: 2
      }]
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom"
        },
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
  if (!chartData.monthLabels.length) {
    emptyChart("monthlyChart", "Add trades to see monthly performance.");
    return;
  }

  new Chart(document.getElementById("monthlyChart"), {
    type: "bar",
    data: {
      labels: chartData.monthLabels,
      datasets: [{
        label: "Profit/Loss",
        data: chartData.monthValues,
        backgroundColor: chartData.monthValues.map(value => value >= 0 ? "#16a34a" : "#dc2626"),
        borderRadius: 4
      }]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: {
            callback: value => rupeeFormatter.format(value)
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: context => rupeeFormatter.format(context.parsed.y)
          }
        }
      }
    }
  });
}

renderIndustryChart();
renderMonthlyChart();
