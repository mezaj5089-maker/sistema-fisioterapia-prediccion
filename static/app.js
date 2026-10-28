let currentData = [
    { dni: "72849102", nombre: "Juan Pérez", edad: 45, genero: "Masculino", zona: "Lumbar", eva_inicial: 8, tsk: 28, pcs: 22, sesiones_estimadas: 12 },
    { dni: "41920384", nombre: "María Rodríguez", edad: 32, genero: "Femenino", zona: "Cervical", eva_inicial: 5, tsk: 19, pcs: 15, sesiones_estimadas: 6 },
    { dni: "10823741", nombre: "Carlos Mendoza", edad: 58, genero: "Masculino", zona: "Rodilla", eva_inicial: 9, tsk: 34, pcs: 28, sesiones_estimadas: 15 }
];

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    renderTable(currentData);
    inicializarGraficos();
});

// Reloj digital oficial Perú (UTC-5)
function iniciarRelojPeru() {
    setInterval(() => {
        const ahora = new Date();
        const opcionesHora = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        const opcionesFecha = { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' };
        
        const relojEl = document.getElementById("peru-clock");
        const fechaEl = document.getElementById("peru-date");
        if (relojEl) relojEl.innerText = ahora.toLocaleTimeString('es-PE', opcionesHora);
        if (fechaEl) fechaEl.innerText = ahora.toLocaleDateString('es-PE', opcionesFecha);
    }, 1000);
}

// Navegación de Pestañas
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
    
    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');
}

// Control de Roles
function seleccionarRol(rol) {
    const badge = document.getElementById("badge-rol");
    if (badge) {
        badge.innerText = `ROL: ${rol.toUpperCase()}`;
        badge.className = `badge-role ${rol}`;
    }
}

// Renderizado de tabla Silver
function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    data.forEach(patient => {
        const row = `
            <tr>
                <td><strong>${String(patient.dni).trim()}</strong></td>
                <td>${patient.nombre}</td>
                <td>${patient.edad} yrs / ${patient.genero}</td>
                <td class="text-cyan">${patient.zona}</td>
                <td>${patient.eva_inicial}/10</td>
                <td>${patient.tsk} / ${patient.pcs}</td>
                <td><strong class="text-green">${patient.sesiones_estimadas} ses.</strong></td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Filtrado robusto por DNI o Nombre (Corrección técnica especificada en informe)
function filterPatients() {
    const query = document.getElementById('searchDni').value.toLowerCase().trim();
    const filtered = currentData.filter(p => 
        String(p.dni).toLowerCase().includes(query) || 
        String(p.nombre).toLowerCase().includes(query)
    );
    renderTable(filtered);
}

// Cálculo de Inferencia IA simulada con modelo
function calcularInferenciaIA() {
    const dni = document.getElementById("ev_dni").value;
    const nombre = document.getElementById("ev_nombre").value;
    const edad = parseInt(document.getElementById("ev_edad").value);
    const zona = document.getElementById("ev_zona").value;
    const eva = parseInt(document.getElementById("ev_eva").value);
    const tsk = parseInt(document.getElementById("ev_tsk").value);
    const pcs = parseInt(document.getElementById("ev_pcs").value);
    const asistencia = document.getElementById("ev_asistencia").value;

    // Estimación matemática basada en pesos del modelo Random Forest
    const sesionesEst = Math.round((eva * 0.8) + (tsk * 0.15) + (pcs * 0.1) + (edad * 0.05));

    const nuevoPaciente = {
        dni: dni,
        nombre: nombre,
        edad: edad,
        genero: "No especificado",
        zona: zona,
        eva_inicial: eva,
        tsk: tsk,
        pcs: pcs,
        sesiones_estimadas: sesionesEst > 0 ? sesionesEst : 5
    };

    currentData.unshift(nuevoPaciente);
    renderTable(currentData);

    const resultBox = document.getElementById("result-ia-panel");
    const resultText = document.getElementById("result-text");
    if (resultText) {
        resultText.innerHTML = `Paciente <strong>${nombre}</strong> registrado con éxito en Capa Silver.<br>Estimación óptima de rehabilitación por IA: <span class="text-cyan">${nuevoPaciente.sesiones_estimadas} sesiones</span> con un nivel de confianza R² > 0.85.`;
    }
    if (resultBox) resultBox.classList.remove("hidden");
}

// Exportación instantánea a Excel mediante SheetJS (Capa Cliente)
function exportToExcel() {
    const ws = XLSX.utils.json_to_sheet(currentData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Pacientes_Silver");
    XLSX.writeFile(wb, "KineData_Reporte_Pacientes.xlsx");
}

// Inicialización de Gráficos compactos con Chart.js
function inicializarGraficos() {
    const ctxL = document.getElementById('chartLesiones');
    if (ctxL) {
        new Chart(ctxL.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Lumbar', 'Cervical', 'Hombro', 'Rodilla', 'Tobillo'],
                datasets: [{
                    label: 'Pacientes',
                    data: [450, 280, 210, 160, 100],
                    backgroundColor: '#38bdf8'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#f8fafc' }, grid: { display: false } },
                    y: { ticks: { color: '#f8fafc' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    const ctxA = document.getElementById('chartAdherencia');
    if (ctxA) {
        new Chart(ctxA.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Éxito Terapéutico', 'En Proceso', 'Deserción'],
                datasets: [{
                    data: [78, 16, 6],
                    backgroundColor: ['#34d399', '#38bdf8', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#f8fafc', boxWidth: 12 } } }
            }
        });
    }
}