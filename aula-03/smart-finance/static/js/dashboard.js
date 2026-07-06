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
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.1)'
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: '#2a2a35' } }, x: { grid: { color: '#2a2a35' } } }
        }
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Receitas', 'Despesas'],
            datasets: [{
                data: [parseFloat(data.totalIncome), parseFloat(data.totalExpense)],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: { cutout: '75%', plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } } }
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
