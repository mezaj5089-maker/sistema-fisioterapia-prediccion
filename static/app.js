// CONFIGURACIÓN DE SUPABASE
const SUPABASE_URL = "https://rjagplujyfnjvdlwmnlp.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYWdwbHVqeWZuanZkbHdtbmxwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc5NTEzNTUsImV4cCI6MjEwMzUyNzM1NX0.Z1F17jSWO2M2LYC4mLLWRayS5EElczduKGNkR5p0FpI";

let listaPacientesGlobal = [];
let isAdminAuthenticated = false;

let barChartInstance = null;
let donutChartInstance = null;

// RELOJ DIGITAL
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
        filtrarPeriodo('semana', document.querySelector('.btn-filter.active'));
    }
}

function hidePanels() {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
}

// OBTENCIÓN DE PACIENTES DE SUPABASE
async function cargarPacientesDesdeSupabase() {
    const tbody = document.getElementById('tbl-silver-body');
    if(tbody) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--accent-cyan);">⏳ Cargando datos desde Supabase...</td></tr>`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

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
            if(listaPacientesGlobal.length === 0) usarPacientesPorDefecto();
            else {
                renderTablaSilver(listaPacientesGlobal);
                actualizarMetricasDashboardReales();
            }
        } else usarPacientesPorDefecto();
    } catch (err) {
        usarPacientesPorDefecto();
    }
}

function usarPacientesPorDefecto() {
    listaPacientesGlobal = [
        { id: 2, dni: "76543310", nombre: "Olivia Estupiñan Segarra", edad: 65, genero: "Femenino", zona_afectada: "Hombro", eva_inicial: 8, tsk_score: 28, pcs_score: 22, num_sesiones: 18 },
        { id: 3, dni: "76010018", nombre: "christian henry", edad: 25, genero: "Masculino", zona_afectada: "Lumbar", eva_inicial: 6, tsk_score: 25, pcs_score: 20, num_sesiones: 14 },
        { id: 4, dni: "49665455", nombre: "Fernando Cacerez Lapa", edad: 25, genero: "Masculino", zona_afectada: "Rodilla", eva_inicial: 7, tsk_score: 30, pcs_score: 18, num_sesiones: 16 }
    ];
    renderTablaSilver(listaPacientesGlobal);
    actualizarMetricasDashboardReales();
}

function renderTablaSilver(pacientes) {
    const tbody = document.getElementById('tbl-silver-body');
    if(!tbody) return;

    let rowsHTML = "";
    pacientes.forEach(p => {
        rowsHTML += `<tr>
            <td style="color:var(--accent-cyan); font-weight:bold;">${p.dni || '--'}</td>
            <td><b>${p.nombre || 'Sin nombre'}</b></td>
            <td>${p.edad || 30} yrs / ${p.genero || 'Masculino'}</td>
            <td><span style="color:var(--accent-purple);">${p.zona_afectada || 'Hombro'}</span></td>
            <td>${p.eva_inicial || 6}/10</td>
            <td>${p.tsk_score || 28} / ${p.pcs_score || 22}</td>
            <td><b style="color:var(--accent-green);">${p.num_sesiones || 14} ses.</b></td>
        </tr>`;
    });
    tbody.innerHTML = rowsHTML;
}

// EXPORTACIONES A EXCEL Y CSV
function descargarExcel() {
    if(!listaPacientesGlobal || listaPacientesGlobal.length === 0) return alert("⚠️ No hay datos.");

    const datosExcel = listaPacientesGlobal.map(p => ({
        "ID": p.id,
        "DNI": p.dni,
        "Nombre Completo": p.nombre,
        "Edad": p.edad,
        "Género": p.genero,
        "Zona Afectada": p.zona_afectada,
        "EVA Inicial": p.eva_inicial,
        "TSK Score": p.tsk_score,
        "PCS Score": p.pcs_score,
        "Sesiones Estimadas": p.num_sesiones
    }));

    const worksheet = XLSX.utils.json_to_sheet(datosExcel);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Pacientes");
    XLSX.writeFile(workbook, `Pacientes_Supabase_${new Date().toISOString().split('T')[0]}.xlsx`);
}

function descargarCSV() {
    if(!listaPacientesGlobal || listaPacientesGlobal.length === 0) return alert("⚠️ No hay datos.");

    let csvContent = "\uFEFFID,DNI,Nombre,Edad,Genero,Zona Afectada,EVA Inicial,TSK Score,PCS Score,Num Sesiones\n";
    listaPacientesGlobal.forEach(p => {
        csvContent += [p.id, `"${p.dni}"`, `"${p.nombre}"`, p.edad, `"${p.genero}"`, `"${p.zona_afectada}"`, p.eva_inicial, p.tsk_score, p.pcs_score, p.num_sesiones].join(",") + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `Pacientes_Supabase_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
}

// BÚSQUEDA CORREGIDA DNI CON AUTO-FETCH Y TRIMMING
async function buscarPacienteDNI() {
    const dniInput = document.getElementById('dni-consulta').value.trim();
    if(!dniInput) return alert("Por favor ingrese un DNI.");

    if (!listaPacientesGlobal || listaPacientesGlobal.length === 0) {
        await cargarPacientesDesdeSupabase();
    }

    const p = listaPacientesGlobal.find(item => String(item.dni).trim() === String(dniInput).trim());

    if (p) {
        document.getElementById('resultado-paciente').style.display = 'block';
        document.getElementById('res-nombre').innerText = p.nombre || 'Paciente';
        document.getElementById('res-dni').innerText = p.dni;
        document.getElementById('res-zona').innerText = p.zona_afectada || 'Hombro';
        document.getElementById('res-eva').innerText = `${p.eva_inicial || 6} / 10`;
        document.getElementById('res-sesiones').innerText = `${p.num_sesiones || 14} Sesiones`;
    } else {
        alert("⚠️ No se encontró el expediente del DNI ingresado.");
    }
}

// MODELO 3D (THREE.JS)
let currentMesh, currentMaterial;
function initThreeJS() {
    const container = document.getElementById('three-container');
    if(!container || container.children.length > 0) return;

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

function actualizarZona3D(val) {
    document.getElementById('badge-zona-desc').innerText = `Dolencia activa: ${val}`;
    if (currentMesh && currentMaterial) {
        const colors = { Hombro: 0x38bdf8, Lumbar: 0xc084fc, Rodilla: 0x34d399, Cervical: 0xf59e0b, Tobillo: 0xec4899 };
        currentMaterial.color.setHex(colors[val] || 0x38bdf8);
    }
}

function actualizarMetricasDashboardReales() {
    const elTotal = document.getElementById('stat-total-pacientes');
    if(elTotal) elTotal.innerText = listaPacientesGlobal.length;
}

// CARGA AUTOMÁTICA
cargarPacientesDesdeSupabase();