// dashboard.js
(async function protectDashboard() {
  try {
    const response = await fetch("http://localhost:5000/api/admin/session", {
      method: "GET",
      credentials: "include"
    });

    if (!response.ok) {
      window.location.href = "/adminlogin/index.html";
    }
  } catch (error) {
    console.error("Admin session check failed:", error);
    window.location.href = "/adminlogin/index.html";
  }
})();


// Get current month and year
const today = new Date();
const currentMonth = today.getMonth() + 1; // JS months are 0-indexed
const currentYear = today.getFullYear();
// dashboard.js

//const currentMonth = 10;
//const currentYear = 2025;


// ---------------- FETCHERS ----------------

async function fetchCardAnalytics() {
    try {
        const response = await fetch(`http://localhost:5000/analytics?month=${currentMonth}&year=${currentYear}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error("Error fetching analytics data:", err);
        return null;
    }
}

async function fetchOverviewAnalytics() {
    try {
        const response = await fetch(`http://localhost:5000/analytics/overview?month=${currentMonth}&year=${currentYear}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error("Error fetching overview analytics:", err);
        return null;
    }
}
async function fetchPredictions() {
    try {
        const response = await fetch(`http://localhost:5000/analytics/predictions?month=${currentMonth}&year=${currentYear}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error("Error fetching predictions data:", err);
        return null;
    }
}


// ---------------- CARDS ----------------

function populateCards(data) {
    if (!data) return;

    document.getElementById('top-cafe-name').textContent = data.top_cafe || "N/A";
    document.getElementById('top-cafe-sales').textContent = "";

    document.getElementById('top-product-name').textContent = data.top_product || "N/A";
    document.getElementById('top-product-sales').textContent = data.top_product_sales
        ? `Sold: ${data.top_product_sales}`
        : "";

    document.getElementById('total-sales').textContent = `${Number(data.total_sales || 0).toLocaleString("fr-FR",{ minimumFractionDigits : 2})} DH`;
        // Growth rate vs last month with +/− and icon
    const growthEl = document.getElementById('growth-rate');
    const growth = data.growth_percent || 0;
    const isPositive = growth >= 0;
    const icon = isPositive ? "⬆️" : "⬇️";
    growthEl.textContent = `${icon} ${isPositive ? "+" : ""}${growth.toFixed(2)}%`;
    growthEl.style.color = isPositive ? "green" : "red";
}

// ---------------- CHARTS ----------------


function renderOverviewCharts(data) {
    console.log("Overview:", data);

    // ===============================
    // 1️⃣ SALES TREND PER CAFÉ
    // ===============================

    const trendCtx = document.getElementById("chart-sales-trend").getContext("2d");

    const trendDatasets = data.sales_per_cafe_daily.map((cafe, i) => ({
        label: cafe.cafe,
        data: cafe.totals,
        borderWidth: 3,
        fill: false,
        tension: 0.25
    }));

    new Chart(trendCtx, {
        type: "line",
        data: {
            labels: data.sales_per_cafe_daily[0].dates,
            datasets: trendDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, 
            plugins: {
                title: { display: true, text: "Daily Sales Trend per Café (DH)" },
                legend: { position: "top" },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} DH`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Sales (DH)" },
                    ticks: { callback: value => value }
                },
                x: {
                    title: { display: true, text: "Day of Month" }
                }
            }
        }
    });

    // ===============================
    // 2️⃣ CAFÉ COMPARISON
    // ===============================

    const compCtx = document.getElementById("chart-cafe-comparison").getContext("2d");

    new Chart(compCtx, {
        type: "bar",
        data: {
            labels: data.cafe_comparison.map(c => c.cafe),
            datasets: [{
                label: "Total Sales (DH)",
                data: data.cafe_comparison.map(c => c.total_sales)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, 
            plugins: {
                title: { display: true, text: "Total Sales per Café (DH)" },
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.label}: ${ctx.raw} DH`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Sales (DH)" },
                    ticks: { callback: value => value  }
                }
            }
        }
    });

    // ===============================
    // 3️⃣ TOP & LEAST PRODUCTS PER CAFÉ
    // ===============================

    const prodCtx = document.getElementById("chart-products").getContext("2d");

    new Chart(prodCtx, {
        type: "bar",
        data: {
            labels: data.top_products_per_cafe.map(t => t.cafe),
            datasets: [
                {
                    label: "Top Product Qty",
                    data: data.top_products_per_cafe.map(t => t.qty)
                },
                {
                    label: "Least Product Qty",
                    data: data.least_products_per_cafe.map(t => t.qty)
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, 
            plugins: {
                title: { display: true, text: "Top & Least Products per Café" },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const arr = ctx.datasetIndex === 0
                                ? data.top_products_per_cafe
                                : data.least_products_per_cafe;

                            return `${arr[ctx.dataIndex].product}: ${ctx.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Quantity Sold" }
                }
            }
        }
    });

    // ===============================
    // 4️⃣ CATEGORY PIE CHART
    // ===============================

    const catCtx = document.getElementById("chart-categories").getContext("2d");
    
    new Chart(catCtx, {
        type: "pie",
        data: {
            labels: data.category_distribution.map(c => c.category),
            datasets: [{
                data: data.category_distribution.map(c => c.total)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: "Sales by Category (DH)" },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const dataset = ctx.chart.data.datasets[0].data;
                            const total = dataset.reduce((a, b) => a + b, 0);
                            const value = ctx.raw;
                            const percent = ((value / total) * 100).toFixed(2);
    
                            return `${ctx.label}: ${value} DH (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderPredictionsChart(predictions) {
    if (!predictions || predictions.length === 0) return;

    const ctx = document.getElementById("chart-predictions").getContext("2d");

    const labels = predictions.map(p => p.cafe_name);
    const currentSales = predictions.map(p => p.current_sales);
    const predictedSales = predictions.map(p => p.predicted_sales);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Current Sales (DH)",
                    data: currentSales,
                    backgroundColor: "#36A2EB"
                },
                {
                    label: "Predicted Sales (DH)",
                    data: predictedSales,
                    backgroundColor: "#FF6384"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: "Current vs Predicted Sales per Café" },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const value = ctx.raw;
                            return `${ctx.dataset.label}: ${value} DH`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Sales (DH)" }
                }
            }
        }
    });
}
function renderPerformanceTable(predictions) {
    if (!predictions || predictions.length === 0) return;

    const tbody = document.querySelector("#prediction-table tbody");
    tbody.innerHTML = "";

    predictions.forEach(p => {
        const isPositive = p.growth_percent >= 0;
        const icon = isPositive ? "⬆️" : "⬇️";
        const growthText = `${icon} ${isPositive ? "+" : ""}${p.growth_percent.toFixed(2)}%`;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${p.rank}</td>
            <td>${p.cafe_name}</td>
            <td>${p.predicted_sales.toFixed(2)} DH</td>
            <td style="color:${isPositive ? 'green':'red'}">${growthText}</td>
        `;
        tbody.appendChild(row);
    });
}

// ---------------- INIT ----------------

async function initDashboard() {
    const cardData = await fetchCardAnalytics();
    if (cardData) populateCards(cardData);

    const overview = await fetchOverviewAnalytics();
    console.log("OVERVIEW DATA:", overview);
    
    if (overview) renderOverviewCharts(overview);
    const predictions = await fetchPredictions();
    if (predictions) {
        renderPredictionsChart(predictions);
        renderPerformanceTable(predictions);
    }
}

initDashboard();

