document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('transaction-search');
    const typeFilter = document.getElementById('type-filter');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const tbody = document.getElementById('transaction-tbody');

    if (!tbody) return;

    const paginationContainer = document.getElementById('pagination-container');
    const pageStart = document.getElementById('page-start');
    const pageEnd = document.getElementById('page-end');
    const totalItems = document.getElementById('total-items');
    const pageNumbers = document.getElementById('page-numbers');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');

    let currentPage = 1;
    let debounceTimer = null;

    function fetchTransactions(page = 1) {
        const query = searchInput.value.trim();
        const type = typeFilter.value;
        const startDate = startDateInput ? startDateInput.value : '';
        const endDate = endDateInput ? endDateInput.value : '';

        // Add loading state to table
        tbody.style.opacity = '0.5';
        tbody.style.pointerEvents = 'none';

        const url = new URL(window.location.href);
        url.searchParams.set('ajax', 'true');
        url.searchParams.set('page', page);
        if (query) url.searchParams.set('search', query);
        if (type !== 'all') url.searchParams.set('type', type);
        if (startDate) url.searchParams.set('start_date', startDate);
        if (endDate) url.searchParams.set('end_date', endDate);

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                renderTable(data.transactions);
                renderPagination(data.pagination);
                currentPage = data.pagination.current_page;

                tbody.style.opacity = '1';
                tbody.style.pointerEvents = 'auto';
            })
            .catch(error => {
                console.error('Error fetching transactions:', error);
                tbody.style.opacity = '1';
                tbody.style.pointerEvents = 'auto';
            });
    }

    function renderTable(transactions) {
        tbody.innerHTML = '';

        if (transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-slate-500 dark:text-slate-400 py-16 px-4">
                        <div class="flex flex-col items-center gap-3">
                            <i class="fa-solid fa-magnifying-glass text-[2.5rem] opacity-30"></i>
                            <p class="text-[0.95rem]">Nenhuma transação encontrada.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        transactions.forEach(tx => {
            const tr = document.createElement('tr');
            tr.className = 'tx-row transition-colors duration-200 hover:bg-slate-50 dark:hover:bg-slate-950';
            tr.setAttribute('data-type', tx.type);

            const badgeClass = tx.type === 'receita' ? 'bg-green-500/10 text-green-600 dark:text-green-500' : 'bg-red-500/10 text-red-600 dark:text-red-500';
            const badgeText = tx.type === 'receita' ? 'Receita' : 'Despesa';
            const textClass = tx.type === 'receita' ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500';

            tr.innerHTML = `
                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 text-[0.95rem]">${tx.date}</td>
                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 font-medium text-slate-900 dark:text-slate-50">${tx.description}</td>
                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 text-[0.95rem]">${tx.category}</td>
                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-center">
                    <span class="py-1.5 px-2.5 rounded-md text-[0.75rem] font-semibold uppercase tracking-wider ${badgeClass}">${badgeText}</span>
                </td>
                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 font-semibold text-right ${textClass}">
                    ${tx.amount_formatted}
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderPagination(pagination) {
        if (!paginationContainer) return;

        if (pageStart) pageStart.textContent = pagination.start_index;
        if (pageEnd) pageEnd.textContent = pagination.end_index;
        if (totalItems) totalItems.textContent = pagination.total_items;

        if (prevBtn) prevBtn.disabled = !pagination.has_previous;
        if (nextBtn) nextBtn.disabled = !pagination.has_next;

        if (pageNumbers) {
            pageNumbers.innerHTML = '';

            let startPage = Math.max(1, pagination.current_page - 2);
            let endPage = Math.min(pagination.total_pages, startPage + 4);

            if (endPage - startPage < 4) {
                startPage = Math.max(1, endPage - 4);
            }

            for (let i = startPage; i <= endPage; i++) {
                const btn = document.createElement('button');
                const activeClass = i === pagination.current_page ? 'bg-teal-600 text-white font-medium border-teal-600' : 'bg-transparent border-transparent text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-950 hover:text-slate-900 dark:hover:text-slate-50';
                btn.className = `w-8 h-8 rounded-md flex items-center justify-center cursor-pointer transition-all duration-200 text-[0.9rem] border ${activeClass}`;
                btn.textContent = i;
                btn.addEventListener('click', () => {
                    if (i !== pagination.current_page) {
                        fetchTransactions(i);
                    }
                });
                pageNumbers.appendChild(btn);
            }
        }

        // Show/hide pagination container based on content
        if (pagination.total_items <= 10 && !searchInput.value && typeFilter.value === 'all') {
            paginationContainer.style.display = 'none';
        } else {
            paginationContainer.style.display = 'flex';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => fetchTransactions(1), 300);
        });
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', () => {
            fetchTransactions(1);
        });
    }

    if (startDateInput) {
        startDateInput.addEventListener('change', () => {
            fetchTransactions(1);
        });
    }

    if (endDateInput) {
        endDateInput.addEventListener('change', () => {
            fetchTransactions(1);
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) fetchTransactions(currentPage - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            fetchTransactions(currentPage + 1);
        });
    }

    // Initialize state on load
    fetchTransactions(1);
});
