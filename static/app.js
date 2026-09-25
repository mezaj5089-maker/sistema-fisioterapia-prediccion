// CONFIGURACIÓN REAL DE SUPABASE
const SUPABASE_URL = "https://rjagplujyfnjvdlwmnlp.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYWdwbHVqeWZuanZkbHdtbmxwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc5NTEzNTUsImV4cCI6MjEwMzUyNzM1NX0.Z1F17jSWO2M2LYC4mLLWRayS5EElczduKGNkR5p0FpI";

// RELOJ DIGITAL DE PERÚ EN VIVO
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

// CONMUTADOR PACIENTE / ADMIN CON LOGIN
function setMode(mode) {
    document.getElementById('btn-paciente').classList.remove('active');
    document.getElementById('btn-admin').classList.remove('active');
    
    if(mode === 'paciente') {
        document.getElementById('btn-paciente').classList.add('active');
        document.getElementById('admin-tabs').style.display = 'none';
        hidePanels();
        document.getElementById('view-paciente-section').classList.add('active');
    } else {
        const password = prompt("🔒 Acceso Restringido Admin/Fisio - Ingrese la contraseña:");
        if (password === "fisio2026" || password === "admin") {
            document.getElementById('btn-admin').classList.add('active');
            document.getElementById('admin-tabs').style.display = 'flex';
            hidePanels();
            document.getElementById('tab-bronze').classList.add('active');
            initThreeJS();
        } else {
            alert("❌ Contraseña incorrecta.");
            setMode('paciente');
        }
    }
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    hidePanels();
    document.getElementById(tabId).classList.add('active');
    if(tabId === 'tab-analytics') initCharts();
}

function hidePanels() {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
}

function actualizarZona3D(val) {
    document.getElementById('lbl-zona-3d').innerText = val;
}

// GUARDA PACIENTE EN SUPABASE
async function guardarPacienteSupabase(e) {
    e.preventDefault();

    const dniVal = document.getElementById('inp-dni').value.trim();
    const nombreVal = document.getElementById('inp-nombre').value.trim();
    const edadVal = parseInt(document.getElementById('inp-edad').value, 10) || 34;
    const generoVal = document.getElementById('inp-genero').value;
    const zonaVal = document.getElementById('inp-zona').value;
    
    // ENTEROS ESTRICTOS (Resuelve el error 22P02 de Supabase)
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
            alert(`✅ ¡Paciente ${nombreVal} guardado con éxito en Supabase! (${sesionesCalc} sesiones estimadas).`);
            
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

            document.getElementById('gold-paciente').innerText = nombreVal;
            document.getElementById('gold-sub').innerText = `DNI: ${dniVal} | Zona: ${zonaVal}`;
            document.getElementById('gold-sesiones').innerText = `${sesionesCalc} Sesiones`;
            document.getElementById('gold-prob').innerText = `${probCalc}%`;

            document.getElementById('form-registro-paciente').reset();
        } else {
            const errData = await response.json();
            alert(`❌ Error al guardar en Supabase: ${errData.message || JSON.stringify(errData)}`);
        }
    } catch (err) {
        alert(`❌ Error de conexión: ${err.message}`);
    }
}

// CONSULTA PACIENTE POR DNI
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

// MODELADO 3D THREE.JS
function initThreeJS() {
    const container = document.getElementById('three-container');
    if(!container || container.children.length > 1) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.CylinderGeometry(0.8, 0.6, 2.5, 16);
    const material = new THREE.MeshBasicMaterial({ color: 0xc084fc, wireframe: true });
    const cylinder = new THREE.Mesh(geometry, material);
    scene.add(cylinder);

    camera.position.z = 4;
    function animate() {
        requestAnimationFrame(animate);
        cylinder.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();
}

// GRÁFICOS CHART.JS
let chartsLoaded = false;
function initCharts() {
    if(chartsLoaded) return;
    chartsLoaded = true;

    const ctxBar = document.getElementById('barChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Hombro', 'Rodilla', 'Lumbar', 'Cervical', 'Tobillo'],
            datasets: [{ label: 'Sesiones', data: [16, 20, 14, 0, 0], backgroundColor: '#38bdf8' }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Hombro', 'Rodilla', 'Lumbar'],
            datasets: [{ data: [1, 1, 1], backgroundColor: ['#38bdf8', '#c084fc', '#ec4899'] }]
        },
        options: { responsive: true }
    });
}