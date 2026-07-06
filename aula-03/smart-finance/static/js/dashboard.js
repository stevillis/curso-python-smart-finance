document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('dashboard-data');
    if (!dataElement) return;

    const data = JSON.parse(dataElement.textContent);

    const ctxFlow = document.getElementById('cashflowChart').getContext('2d');
    new Chart(ctxFlow, {
        type: 'line',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
            datasets: [{
                label: 'Saldo',
                data: [0, 0, 0, 0, parseFloat(data.currentBalance)],
                borderColor: '#10b981',
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#10b981'
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: '#0f172a', padding: 12, cornerRadius: 8 }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { display: false },
                    border: { display: false },
                    ticks: { color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: { color: '#64748b' }
                }
            }
        }
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    new Chart(ctxDonut, {
        type: 'bar',
        data: {
            labels: ['Receitas', 'Despesas'],
            datasets: [{
                data: [parseFloat(data.totalIncome), parseFloat(data.totalExpense)],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0,
                borderRadius: 4,
                barThickness: 32
            }]
        },
        options: {
            indexAxis: 'y',
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: '#0f172a', padding: 12, cornerRadius: 8 }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { display: false },
                    border: { display: false },
                    ticks: { display: false }
                },
                y: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: { color: '#64748b', font: { weight: '500' } }
                }
            }
        }
    });

    // Fetch AI Insight
    fetch(data.insightUrl)
        .then(res => res.json())
        .then(resData => {
            document.getElementById('ai-insight').innerText = resData.insight;
        })
        .catch(err => {
            document.getElementById('ai-insight').innerText = "Insight indisponível.";
        });
});
