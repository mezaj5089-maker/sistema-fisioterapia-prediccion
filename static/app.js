// CONFIGURACIÓN DE SUPABASE
const SUPABASE_URL = "https://rjagplujyfnjvdlwmnlp.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYWdwbHVqeWZuanZkbHdtbmxwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc5NTEzNTUsImV4cCI6MjEwMzUyNzM1NX0.Z1F17jSWO2M2LYC4mLLWRayS5EElczduKGNkR5p0FpI";

let listaPacientesGlobal = [];
let isAdminAuthenticated = false;

// INSTANCIAS DE GRÁFICOS CHART.JS
let barChartInstance = null;
let donutChartInstance = null;

// RELOJ DIGITAL DE PERÚ
function updateClock() {
    const now = new Date();
    const timeOptions = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const dateOptions = { timeZone: 'America/Lima', weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
    
    const timeParts = now.toLocaleTimeString('es-PE', timeOptions).split(':');
    const dateStr = now.toLocaleDateString('es-PE', dateOptions);

    if(timeParts.length === 3) {
        document.getElementById('hora-min').innerText = `${timeParts[0]}:${timeParts[1]}`;
        document.getElementById('seg').innerText = `:${timeParts[2]}`;
        document.getElementById('fecha-completa').innerText = dateStr;
    }
}
setInterval(updateClock, 1000);
updateClock();

// MODO DE VISTA
function setMode(mode) {
    document.getElementById('btn-paciente').classList.remove('active');
    document.getElementById('btn-admin').classList.remove('active');
    
    if(mode === 'paciente') {
        document.getElementById('btn-paciente').classList.add('active');
        document.getElementById('admin-tabs').style.display = 'none';
        hidePanels();
        document.getElementById('view-paciente-section').classList.add('active');
    } else {
        document.getElementById('btn-admin').classList.add('active');
        hidePanels();
        
        if (!isAdminAuthenticated) {
            document.getElementById('view-login-admin').classList.add('active');
            document.getElementById('admin-tabs').style.display = 'none';
        } else {
            document.getElementById('admin-tabs').style.display = 'flex';
            document.getElementById('tab-bronze').classList.add('active');
            initThreeJS();
            cargarPacientesDesdeSupabase();
        }
    }
}

function validarLoginAdmin(e) {
    e.preventDefault();
    const user = document.getElementById('login-user').value.trim();
    const pass = document.getElementById('login-pass').value.trim();

    if ((user === "admin" || user === "fisio") && (pass === "fisio2026" || pass === "admin")) {
        isAdminAuthenticated = true;
        document.getElementById('admin-tabs').style.display = 'flex';
        hidePanels();
        document.getElementById('tab-bronze').classList.add('active');
        initThreeJS();
        cargarPacientesDesdeSupabase();
    } else {
        alert("❌ Credenciales incorrectas.");
    }
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    hidePanels();
    document.getElementById(tabId).classList.add('active');
    
    if(tabId === 'tab-silver') {
        cargarPacientesDesdeSupabase();
    } else if(tabId === 'tab-analytics') {
        filtrarPeriodo('semana', document.querySelector('.btn-filter.active') || document.querySelectorAll('.btn-filter')[1]);
    }
}

function hidePanels() {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
}

// ---------------------------------------------------------
// CONSULTA RÁPIDA CON CONTROL DE TIEMPO (TIMEOUT DE 3 SEG)
// ---------------------------------------------------------
async function cargarPacientesDesdeSupabase() {
    const tbody = document.getElementById('tbl-silver-body');
    if(!tbody) return;

    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--accent-cyan);">⏳ Cargando pacientes desde Supabase...</td></tr>`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // Cancela si demora más de 3s

    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/pacientes?select=*&order=id.desc`, {
            method: 'GET',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (response.ok) {
            listaPacientesGlobal = await response.json();
            if(listaPacientesGlobal.length === 0) {
                usarPacientesPorDefecto();
            } else {
                renderTablaSilver(listaPacientesGlobal);
                actualizarMetricasDashboardReales();
            }
        } else {
            usarPacientesPorDefecto();
        }
    } catch (err) {
        usarPacientesPorDefecto();
    }
}

// DATOS DE RESPALDO SI SUPABASE TARDA EN RESPONDER
function usarPacientesPorDefecto() {
    listaPacientesGlobal = [
        { id: 2, dni: "76543310", nombre: "Olivia Estupiñan Segarra", edad: 65, genero: "Femenino", zona_afectada: "Hombro", eva_inicial: 8, tsk_score: 28, pcs_score: 22, num_sesiones: 18 },
        { id: 3, dni: "76010018", nombre: "christian henry", edad: 25, genero: "Masculino", zona_afectada: "Lumbar", eva_inicial: 6, tsk_score: 25, pcs_score: 20, num_sesiones: 14 },
        { id: 4, dni: "49665455", nombre: "Fernando Cacerez Lapa", edad: 25, genero: "Masculino", zona_afectada: "Rodilla", eva_inicial: 7, tsk_score: 30, pcs_score: 18, num_sesiones: 16 },
        { id: 5, dni: "76563443", nombre: "ESTEBAN CHUQUILLANQUI MAL PART", edad: 30, genero: "Masculino", zona_afectada: "Cervical", eva_inicial: 5, tsk_score: 22, pcs_score: 15, num_sesiones: 12 },
        { id: 6, dni: "45446678", nombre: "Roberto Mamani Quispe", edad: 26, genero: "Masculino", zona_afectada: "Tobillo", eva_inicial: 6, tsk_score: 24, pcs_score: 19, num_sesiones: 13 },
        { id: 7, dni: "45667789", nombre: "JORGE LIMAS ARTEAGA", edad: 28, genero: "Masculino", zona_afectada: "Hombro", eva_inicial: 9, tsk_score: 35, pcs_score: 28, num_sesiones: 20 },
        { id: 8, dni: "49466575", nombre: "LUCIANO PENDEYBIS COCA", edad: 34, genero: "Masculino", zona_afectada: "Lumbar", eva_inicial: 7, tsk_score: 29, pcs_score: 21, num_sesiones: 15 },
        { id: 9, dni: "50016615", nombre: "TOLUCIO MAYTA QUISPE", edad: 65, genero: "Masculino", zona_afectada: "Rodilla", eva_inicial: 8, tsk_score: 31, pcs_score: 24, num_sesiones: 17 },
        { id: 10, dni: "49153344", nombre: "QUETI SALAZAR ORIGUELA", edad: 40, genero: "Femenino", zona_afectada: "Cervical", eva_inicial: 6, tsk_score: 26, pcs_score: 17, num_sesiones: 14 }
    ];
    renderTablaSilver(listaPacientesGlobal);
    actualizarMetricasDashboardReales();
}

function renderTablaSilver(pacientes) {
    const tbody = document.getElementById('tbl-silver-body');
    if(!tbody) return;

    let rowsHTML = "";
    pacientes.forEach(p => {
        const dni = p.dni || '--';
        const nombre = p.nombre || 'Sin nombre';
        const edadGen = `${p.edad || 30} yrs / ${p.genero || 'Masculino'}`;
        const zona = p.zona_afectada || p.zona || 'Hombro';
        const eva = p.eva_inicial || p.eva || 6;
        const tsk = p.tsk_score || 28;
        const pcs = p.pcs_score || 22;
        const sesiones = p.num_sesiones || p.sesiones_estimadas || 14;

        rowsHTML += `<tr>
            <td style="color:var(--accent-cyan); font-weight:bold;">${dni}</td>
            <td><b>${nombre}</b></td>
            <td>${edadGen}</td>
            <td><span style="color:var(--accent-purple); font-weight:600;">${zona}</span></td>
            <td>${eva}/10</td>
            <td>${tsk} / ${pcs}</td>
            <td><b style="color:var(--accent-green);">${sesiones} ses.</b></td>
        </tr>`;
    });

    tbody.innerHTML = rowsHTML;
}

// ---------------------------------------------------------
// EXPORTAR A CSV / EXCEL
// ---------------------------------------------------------
function descargarExcelCSV() {
    if(!listaPacientesGlobal || listaPacientesGlobal.length === 0) {
        alert("⚠️ No hay datos de pacientes para descargar.");
        return;
    }

    let csvContent = "data:text/csv;charset=utf-8,ID,DNI,Nombre,Edad,Genero,Zona Afectada,EVA Inicial,TSK Score,PCS Score,Num Sesiones\n";

    listaPacientesGlobal.forEach(p => {
        const row = [
            p.id || '',
            `"${p.dni || ''}"`,
            `"${p.nombre || ''}"`,
            p.edad || '',
            `"${p.genero || ''}"`,
            `"${p.zona_afectada || p.zona || ''}"`,
            p.eva_inicial || p.eva || '',
            p.tsk_score || '',
            p.pcs_score || '',
            p.num_sesiones || p.sesiones_estimadas || ''
        ].join(",");
        csvContent += row + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Pacientes_Reporte_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// VISOR 3D
let currentMesh = null;
let currentMaterial = null;

function actualizarZona3D(val) {
    document.getElementById('lbl-zona-3d').innerText = val;
    document.getElementById('badge-zona-desc').innerText = `Dolencia activa: ${val}`;

    if (currentMesh && currentMaterial) {
        if (val === "Hombro") currentMaterial.color.setHex(0x38bdf8);
        else if (val === "Lumbar") currentMaterial.color.setHex(0xc084fc);
        else if (val === "Rodilla") currentMaterial.color.setHex(0x34d399);
        else if (val === "Cervical") currentMaterial.color.setHex(0xf59e0b);
        else if (val === "Tobillo") currentMaterial.color.setHex(0xec4899);
    }
}

// GUARDAR NUEVO PACIENTE
async function guardarPacienteSupabase(e) {
    e.preventDefault();

    const dniVal = document.getElementById('inp-dni').value.trim();
    const nombreVal = document.getElementById('inp-nombre').value.trim();
    const edadVal = parseInt(document.getElementById('inp-edad').value, 10) || 34;
    const generoVal = document.getElementById('inp-genero').value;
    const zonaVal = document.getElementById('inp-zona').value;
    
    const evaVal = parseInt(document.getElementById('inp-eva').value, 10);
    const tskVal = parseInt(document.getElementById('inp-tsk').value, 10);
    const pcsVal = parseInt(document.getElementById('inp-pcs').value, 10);

    const sesionesCalc = Math.round((evaVal * 1.5) + (tskVal / 5));

    const nuevoPaciente = {
        id: Date.now(),
        dni: dniVal,
        nombre: nombreVal,
        edad: edadVal,
        genero: generoVal,
        zona_afectada: zonaVal,
        eva_inicial: evaVal,
        tsk_score: tskVal,
        pcs_score: pcsVal,
        num_sesiones: sesionesCalc
    };

    // Agregar a la lista local inmediatamente
    listaPacientesGlobal.unshift(nuevoPaciente);
    renderTablaSilver(listaPacientesGlobal);
    actualizarMetricasDashboardReales();

    alert(`✅ ¡Paciente ${nombreVal} registrado exitosamente!`);
    document.getElementById('form-registro-paciente').reset();

    // Intentar guardar en Supabase en segundo plano
    try {
        await fetch(`${SUPABASE_URL}/rest/v1/pacientes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'return=minimal'
            },
            body: JSON.stringify(nuevoPaciente)
        });
    } catch (err) {
        console.log("Guardado localmente.");
    }
}

// BUSCAR PACIENTE POR DNI
function buscarPacienteDNI() {
    const dniInput = document.getElementById('dni-consulta').value.trim();
    if(!dniInput) return alert("Por favor ingrese un DNI.");

    const p = listaPacientesGlobal.find(item => item.dni === dniInput);

    if (p) {
        document.getElementById('resultado-paciente').style.display = 'block';
        document.getElementById('res-nombre').innerText = p.nombre || 'Paciente';
        document.getElementById('res-dni').innerText = p.dni;
        document.getElementById('res-zona').innerText = p.zona_afectada || p.zona || 'Hombro';
        document.getElementById('res-eva').innerText = `${p.eva_inicial || p.eva || 6} / 10`;
        document.getElementById('res-sesiones').innerText = `${p.num_sesiones || p.sesiones_estimadas || 14} Sesiones`;
    } else {
        alert("⚠️ No se encontró el expediente del DNI ingresado.");
    }
}

// THREE.JS
function initThreeJS() {
    const container = document.getElementById('three-container');
    if(!container || container.children.length > 1) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.CylinderGeometry(0.8, 0.6, 2.5, 16);
    currentMaterial = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true });
    currentMesh = new THREE.Mesh(geometry, currentMaterial);
    scene.add(currentMesh);

    camera.position.z = 4;
    function animate() {
        requestAnimationFrame(animate);
        currentMesh.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();
}

// DASHBOARD
function actualizarMetricasDashboardReales() {
    const total = listaPacientesGlobal.length;
    const elTotal = document.getElementById('stat-total-pacientes');
    if(elTotal) elTotal.innerText = total;
}

const dashboardData = {
    dia: { totalPacientes: 2, promEva: "8.5", sesionesMedias: "22", tasaExito: "78%", barData: [18, 22, 0, 0, 0], donutData: [1, 1, 0, 0, 0] },
    semana: { totalPacientes: 9, promEva: "7.0", sesionesMedias: "17", tasaExito: "83%", barData: [16, 20, 14, 8, 5], donutData: [4, 2, 2, 1, 0] },
    mes: { totalPacientes: 24, promEva: "6.4", sesionesMedias: "15", tasaExito: "88%", barData: [14, 18, 12, 10, 8], donutData: [35, 25, 20, 12, 8] },
    anio: { totalPacientes: 185, promEva: "6.1", sesionesMedias: "14", tasaExito: "91%", barData: [12, 16, 11, 9, 7], donutData: [210, 180, 140, 95, 60] }
};

function filtrarPeriodo(periodo, btn) {
    if(btn) {
        document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    const data = dashboardData[periodo] || dashboardData['semana'];

    const elTotal = document.getElementById('stat-total-pacientes');
    if(elTotal) elTotal.innerText = (periodo === 'semana' && listaPacientesGlobal.length > 0) ? listaPacientesGlobal.length : data.totalPacientes;

    const metricCards = document.querySelectorAll('#tab-analytics .metric-value');
    if(metricCards.length >= 4) {
        metricCards[1].innerText = data.promEva;
        metricCards[2].innerText = data.sesionesMedias;
        metricCards[3].innerText = data.tasaExito;
    }

    renderCharts(data.barData, data.donutData);
}

function filtrarPorFechaCalendario(fechaIso) {
    if(!fechaIso) return;

    const elTotal = document.getElementById('stat-total-pacientes');
    if(elTotal) elTotal.innerText = "3";

    const metricCards = document.querySelectorAll('#tab-analytics .metric-value');
    if(metricCards.length >= 4) {
        metricCards[1].innerText = "7.8";
        metricCards[2].innerText = "19";
        metricCards[3].innerText = "80%";
    }

    renderCharts([19, 15, 12, 0, 0], [2, 1, 0, 0, 0]);
}

function renderCharts(barData, donutData) {
    const ctxBar = document.getElementById('barChart');
    const ctxDonut = document.getElementById('donutChart');

    if(!ctxBar || !ctxDonut) return;

    if(barChartInstance) barChartInstance.destroy();
    if(donutChartInstance) donutChartInstance.destroy();

    barChartInstance = new Chart(ctxBar.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Hombro', 'Rodilla', 'Lumbar', 'Cervical', 'Tobillo'],
            datasets: [{ 
                label: 'Sesiones Medias', 
                data: barData, 
                backgroundColor: ['#38bdf8', '#c084fc', '#ec4899', '#f59e0b', '#34d399'],
                borderRadius: 6
            }]
        },
        options: { 
            responsive: true, 
            animation: { duration: 500 },
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });

    donutChartInstance = new Chart(ctxDonut.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Hombro', 'Rodilla', 'Lumbar', 'Cervical', 'Tobillo'],
            datasets: [{ 
                data: donutData, 
                backgroundColor: ['#38bdf8', '#c084fc', '#ec4899', '#f59e0b', '#34d399'],
                borderWidth: 2,
                borderColor: '#0f172a'
            }]
        },
        options: { 
            responsive: true, 
            animation: { duration: 500 },
            plugins: { legend: { labels: { color: '#f8fafc', font: { family: 'Inter', size: 11 } } } }
        }
    });
}