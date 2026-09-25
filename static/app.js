// CONFIGURACIÓN REAL DE SUPABASE
const SUPABASE_URL = "https://rjagplujyfnjvdlwmnlp.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYWdwbHVqeWZuanZkbHdtbmxwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc5NTEzNTUsImV4cCI6MjEwMzUyNzM1NX0.Z1F17jSWO2M2LYC4mLLWRayS5EElczduKGNkR5p0FpI";

let totalPacientesMemoria = 7;
let isAdminAuthenticated = false;

// VARIABLES PARA INSTANCIAS DE GRÁFICOS (Chart.js)
let barChartInstance = null;
let donutChartInstance = null;

// RELOJ DIGITAL EN VIVO DE PERÚ
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

// CONMUTADOR VISTA PACIENTE / ADMIN CON FORMULARIO LOGIN
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
    } else {
        alert("❌ Credenciales incorrectas. Verifique usuario y contraseña.");
    }
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    hidePanels();
    document.getElementById(tabId).classList.add('active');
    if(tabId === 'tab-analytics') {
        filtrarPeriodo('semana', document.querySelector('.btn-filter.active') || document.querySelectorAll('.btn-filter')[1]);
    }
}

function hidePanels() {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
}

// ACTUALIZACIÓN DE VISOR ANATÓMICO 3D SEGÚN ZONA
let currentMesh = null;
let currentMaterial = null;

function actualizarZona3D(val) {
    document.getElementById('lbl-zona-3d').innerText = val;
    document.getElementById('badge-zona-desc').innerText = `Dolencia activa: ${val}`;

    if (currentMesh && currentMaterial) {
        if (val === "Hombro") {
            currentMaterial.color.setHex(0x38bdf8); // Azul
        } else if (val === "Lumbar") {
            currentMaterial.color.setHex(0xc084fc); // Morado
        } else if (val === "Rodilla") {
            currentMaterial.color.setHex(0x34d399); // Verde
        } else if (val === "Cervical") {
            currentMaterial.color.setHex(0xf59e0b); // Naranja
        } else if (val === "Tobillo") {
            currentMaterial.color.setHex(0xec4899); // Rosa
        }
    }
}

// GUARDA PACIENTE EN SUPABASE Y ACTUALIZA DASHBOARD EN TIEMPO REAL
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
    const probCalc = Math.round(Math.max(30, 100 - (evaVal * 3.2 + tskVal * 0.4 + pcsVal * 0.3)));

    const fechaAlta = new Date();
    fechaAlta.setDate(fechaAlta.getDate() + (sesionesCalc * 2));
    const fechaAltaStr = fechaAlta.toISOString().split('T')[0];

    const payload = {
        dni: dniVal,
        nombre: nombreVal,
        edad: edadVal,
        genero: generoVal,
        zona_afectada: zonaVal,
        eva_inicial: evaVal,
        tsk_score: tskVal,
        pcs_score: pcsVal,
        num_sesiones: sesionesCalc,
        fecha_alta: fechaAltaStr,
        probabilidad_recuperacion: probCalc
    };

    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/pacientes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert(`✅ ¡Paciente ${nombreVal} registrado exitosamente en Supabase!`);
            
            // Actualización inmediata de tabla Capa Silver
            const tbody = document.getElementById('tbl-silver-body');
            if(tbody) {
                const row = `<tr>
                    <td style="color:var(--accent-cyan); font-weight:bold;">${dniVal}</td>
                    <td>${nombreVal}</td>
                    <td>${edadVal} yrs / ${generoVal}</td>
                    <td>${zonaVal}</td>
                    <td>${evaVal}/10</td>
                    <td>${tskVal} / ${pcsVal}</td>
                    <td><b>${sesionesCalc} ses.</b></td>
                </tr>`;
                tbody.innerHTML = row + tbody.innerHTML;
            }

            // Actualización inmediata Capa Gold
            document.getElementById('gold-paciente').innerText = nombreVal;
            document.getElementById('gold-sub').innerText = `DNI: ${dniVal} | Zona: ${zonaVal}`;
            document.getElementById('gold-sesiones').innerText = `${sesionesCalc} Sesiones`;
            document.getElementById('gold-prob').innerText = `${probCalc}%`;

            // Incremento directo de métricas
            totalPacientesMemoria++;
            document.getElementById('stat-total-pacientes').innerText = totalPacientesMemoria;

            document.getElementById('form-registro-paciente').reset();
        } else {
            const errData = await response.json();
            alert(`❌ Error al guardar en Supabase: ${errData.message || JSON.stringify(errData)}`);
        }
    } catch (err) {
        alert(`❌ Error de conexión: ${err.message}`);
    }
}

// CONSULTA PACIENTE POR DNI EN SUPABASE
async function buscarPacienteDNI() {
    const dniInput = document.getElementById('dni-consulta').value.trim();
    if(!dniInput) {
        alert("Por favor ingrese un número de DNI.");
        return;
    }

    try {
        const res = await fetch(`${SUPABASE_URL}/rest/v1/pacientes?dni=eq.${dniInput}`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        const data = await res.json();

        if (data && data.length > 0) {
            const p = data[0];
            document.getElementById('resultado-paciente').style.display = 'block';
            document.getElementById('res-nombre').innerText = p.nombre || 'Paciente';
            document.getElementById('res-dni').innerText = p.dni;
            document.getElementById('res-zona').innerText = p.zona_afectada || p.zona || 'Hombro';
            document.getElementById('res-eva').innerText = `${p.eva_inicial || p.eva || 6} / 10`;
            document.getElementById('res-sesiones').innerText = `${p.num_sesiones || p.sesiones_estimadas || 14} Sesiones`;
        } else {
            alert("⚠️ No se encontró ningún expediente registrado con el DNI ingresado en Supabase.");
        }
    } catch(err) {
        alert("Error al realizar la consulta en Supabase.");
    }
}

// MODELADO 3D INTERACTIVO
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

// ---------------------------------------------------------
// LÓGICA DINÁMICA DE FILTRADO PARA EL DASHBOARD ANALYTICS
// ---------------------------------------------------------

// DICCIONARIOS DE DATOS DINÁMICOS POR PERÍODO
const dashboardData = {
    dia: {
        totalPacientes: 2,
        promEva: "8.5",
        sesionesMedias: "22",
        tasaExito: "78%",
        barData: [18, 22, 0, 0, 0],
        donutData: [1, 1, 0, 0, 0]
    },
    semana: {
        totalPacientes: 7,
        promEva: "7.0",
        sesionesMedias: "17",
        tasaExito: "83%",
        barData: [16, 20, 14, 8, 5],
        donutData: [10, 8, 6, 4, 2]
    },
    mes: {
        totalPacientes: 24,
        promEva: "6.4",
        sesionesMedias: "15",
        tasaExito: "88%",
        barData: [14, 18, 12, 10, 8],
        donutData: [35, 25, 20, 12, 8]
    },
    anio: {
        totalPacientes: 185,
        promEva: "6.1",
        sesionesMedias: "14",
        tasaExito: "91%",
        barData: [12, 16, 11, 9, 7],
        donutData: [210, 180, 140, 95, 60]
    }
};

function filtrarPeriodo(periodo, btn) {
    if(btn) {
        document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    const data = dashboardData[periodo] || dashboardData['semana'];

    // Actualizar Métrica 1
    const elTotal = document.getElementById('stat-total-pacientes');
    if(elTotal) elTotal.innerText = (periodo === 'semana') ? totalPacientesMemoria : data.totalPacientes;

    // Actualizar Métrica 2, 3 y 4
    const metricCards = document.querySelectorAll('#tab-analytics .metric-value');
    if(metricCards.length >= 4) {
        metricCards[1].innerText = data.promEva;
        metricCards[2].innerText = data.sesionesMedias;
        metricCards[3].innerText = data.tasaExito;
    }

    // Renderizar Gráficos dinámicos con la nueva data
    renderCharts(data.barData, data.donutData);
}

function filtrarPorFechaCalendario(fechaIso) {
    if(!fechaIso) return;
    
    // Simulación de cálculo dinámico para fecha específica
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

    // Destruir instancias previas para evitar superposición
    if(barChartInstance) barChartInstance.destroy();
    if(donutChartInstance) donutChartInstance.destroy();

    // Gráfico de Barras Dinámico
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
            animation: { duration: 600 },
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });

    // Gráfico Donut Dinámico
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
            animation: { duration: 600 },
            plugins: {
                legend: { labels: { color: '#f8fafc', font: { family: 'Inter', size: 11 } } }
            }
        }
    });
}