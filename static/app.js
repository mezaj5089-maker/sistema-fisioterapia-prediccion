let chartLinealObj = null;
let chartBarrasObj = null;
let chartCircularObj = null;

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    generarCalendarioWidget();
    inicializarGraficosDashboard();
});

// Reloj Digital Oficial Perú (UTC-5)
function iniciarRelojPeru() {
    setInterval(() => {
        const ahora = new Date();
        const opcionesHora = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        const opcionesFecha = { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' };
        
        document.getElementById("peru-clock").innerText = ahora.toLocaleTimeString('es-PE', opcionesHora);
        document.getElementById("peru-date").innerText = ahora.toLocaleDateString('es-PE', opcionesFecha);
    }, 1000);
}

// Navegación de Pestañas
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(`tab-${tabId}`).classList.add('active');
    document.getElementById(`tab-btn-${tabId}`).classList.add('active');
}

// Inicialización de Gráficos del Dashboard
function inicializarGraficosDashboard() {
    // 1. Gráfico Lineal (Tendencia Temporal)
    const ctxL = document.getElementById('chartLineal').getContext('2d');
    chartLinealObj = new Chart(ctxL, {
        type: 'line',
        data: {
            labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            datasets: [{
                label: 'Evolución de Pacientes Activos',
                data: [30, 45, 60, 85],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: { responsive: true, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
    });

    // 2. Gráfico de Barras (Prevalencia por Lesión)
    const ctxB = document.getElementById('chartBarras').getContext('2d');
    chartBarrasObj = new Chart(ctxB, {
        type: 'bar',
        data: {
            labels: ['Lumbalgia', 'Cervicalgia', 'Articular', 'Post-quirúrgica'],
            datasets: [{
                label: 'Casos Registrados',
                data: [45, 38, 25, 20],
                backgroundColor: ['#38bdf8', '#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: { responsive: true, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
    });

    // 3. Gráfico Circular / Doughnut (Distribución de Riesgo)
    const ctxC = document.getElementById('chartCircular').getContext('2d');
    chartCircularObj = new Chart(ctxC, {
        type: 'doughnut',
        data: {
            labels: ['Bajo Riesgo', 'Riesgo Moderado', 'Alto Riesgo'],
            datasets: [{
                data: [65, 39, 24],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: { responsive: true, plugins: { legend: { labels: { color: '#f8fafc' } } } }
    });
}

// Actualización Reactiva de Gráficos mediante Filtros Temporales (Año, Mes, Día, Hora)
function actualizarDashboardFiltros() {
    const anio = document.getElementById('filtro-anio').value;
    const mes = document.getElementById('filtro-mes').value;
    const dia = document.getElementById('filtro-dia').value;
    const hora = document.getElementById('filtro-hora').value;

    // Simulación de variación dinámica de datos según filtros temporales seleccionados
    let multiplicador = 1.0;
    if (mes !== 'todos') multiplicador *= 0.8;
    if (dia !== 'todos') multiplicador *= 0.6;
    if (hora !== 'todas') multiplicador *= 0.4;

    const nuevasLineas = [30, 45, 60, 85].map(v => Math.round(v * multiplicador));
    const nuevasBarras = [45, 38, 25, 20].map(v => Math.round(v * multiplicador));
    const nuevosCirculares = [65, 39, 24].map(v => Math.round(v * multiplicador));

    chartLinealObj.data.datasets[0].data = nuevasLineas;
    chartLinealObj.update();

    chartBarrasObj.data.datasets[0].data = nuevasBarras;
    chartBarrasObj.update();

    chartCircularObj.data.datasets[0].data = nuevosCirculares;
    chartCircularObj.update();

    document.getElementById('kpi-total').innerText = Math.round(142 * multiplicador);
    document.getElementById('kpi-riesgo').innerText = Math.round(18 * multiplicador);
}

// Motor de Inferencia IA de Machine Learning
function ejecutarInferenciaIA() {
    const tsk = parseInt(document.getElementById("ev-tsk").value);
    const pcs = parseInt(document.getElementById("ev-pcs").value);
    const asistencia = parseInt(document.getElementById("ev-asistencia").value);

    const score = (tsk + pcs) - (asistencia / 2);
    let nivel = "BAJO";

    if (score > 40) nivel = "ALTO";
    else if (score > 20) nivel = "MODERADO";

    const box = document.getElementById("result-ia-panel");
    const badge = document.getElementById("badge-risk-result");
    
    badge.innerText = `RIESGO PREDECIDO: ${nivel}`;
    badge.style.borderColor = nivel === 'ALTO' ? '#ef4444' : (nivel === 'MODERADO' ? '#f59e0b' : '#10b981');
    badge.style.color = badge.style.borderColor;
    
    box.classList.remove("hidden");
}

// Filtrado de Tabla de Pacientes
function filtrarPacientes() {
    const query = document.getElementById("search-dni").value.toLowerCase().trim();
    const filas = document.querySelectorAll("#table-body tr");

    filas.forEach(fila => {
        const texto = fila.innerText.toLowerCase();
        fila.style.display = texto.includes(query) ? "" : "none";
    });
}

// Exportación a Excel (.XLSX)
function exportToExcel() {
    const tabla = document.getElementById("tabla-pacientes");
    const wb = XLSX.utils.table_to_book(tabla, { sheet: "Pacientes_Clinicos" });
    XLSX.writeFile(wb, "KineData_Reporte_Fisioterapia.xlsx");
}

// Calendario Interactivo Dinámico
function generarCalendarioWidget() {
    const widget = document.getElementById("calendar-widget");
    if (!widget) return;
    
    let html = '<div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; text-align:center; font-size:0.85rem;">';
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    
    dias.forEach(d => html += `<strong style="color:var(--accent-cyan);">${d}</strong>`);
    
    for (let i = 1; i <= 31; i++) {
        let style = (i === 24) ? 'background:var(--accent-cyan); color:#000; font-weight:800;' : 'background:rgba(255,255,255,0.05); color:#fff;';
        html += `<div style="padding:10px; border-radius:6px; ${style}">${i}</div>`;
    }
    html += '</div>';
    widget.innerHTML = html;
}

// Reprogramación Anticipada
function reprogramarCita(e) {
    e.preventDefault();
    const dni = document.getElementById("cita-dni").value;
    const fecha = document.getElementById("cita-fecha").value;
    const motivo = document.getElementById("cita-motivo").value;

    alert(`✅ Cita reprogramada con éxito.\nDNI: ${dni}\nNueva Fecha: ${fecha}\nMotivo: ${motivo}`);
}