document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Logic
    const navLinks = document.querySelectorAll('.nav-links li');
    const sections = document.querySelectorAll('main section');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetSection = link.getAttribute('data-section');
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Update active section
            sections.forEach(s => {
                s.classList.remove('active');
                if (s.id === targetSection) {
                    s.classList.add('active');
                }
            });
        });
    });

    // 2. Data Hub (Table) Logic
    let products = [];
    let filteredProducts = [];
    let currentPage = 1;
    const itemsPerPage = 10;

    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageInfo = document.getElementById('pageInfo');

    // Fetch data from data.json
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            products = data;
            filteredProducts = [...products];
            renderTable();
        })
        .catch(err => console.error('Error loading data:', err));

    function renderTable() {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const paginatedItems = filteredProducts.slice(startIndex, endIndex);

        tableBody.innerHTML = '';
        
        paginatedItems.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><a href="${item.itemLnkd}" target="_blank" style="color: inherit; text-decoration: none;">${item.itemNm}</a></td>
                <td>${item.brandNm || '-'}</td>
                <td class="gold-text">${Number(item.displayPrc).toLocaleString()}원</td>
                <td>${Number(item.itemOrdQty).toLocaleString()}</td>
                <td>${item.siteNm || '기타'}</td>
            `;
            tableBody.appendChild(row);
        });

        // Update Pagination Info
        const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
        pageInfo.innerText = `Page ${currentPage} of ${totalPages || 1}`;
        
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    }

    // Search Logic
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        filteredProducts = products.filter(p => 
            p.itemNm.toLowerCase().includes(searchTerm) || 
            (p.brandNm && p.brandNm.toLowerCase().includes(searchTerm))
        );
        currentPage = 1;
        renderTable();
    });

    // Pagination Click Events
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    });

    nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
        }
    });

    // Animation on Load
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});
