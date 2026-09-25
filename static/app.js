// RELOJ DIGITAL EN VIVO DE PERÚ (GMT-5)
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

// CONMUTADOR VISTA PACIENTE / ADMIN CON SEGURIDAD LOGIN
function setMode(mode) {
    document.getElementById('btn-paciente').classList.remove('active');
    document.getElementById('btn-admin').classList.remove('active');
    
    if(mode === 'paciente') {
        document.getElementById('btn-paciente').classList.add('active');
        document.getElementById('admin-tabs').style.display = 'none';
        hidePanels();
        document.getElementById('view-paciente-section').classList.add('active');
    } else {
        // Solicitud de Login de Administrador
        const password = prompt("🔒 Acceso Restringido - Ingrese la Contraseña de Administrador:");
        if (password === "fisio2026" || password === "admin123") {
            document.getElementById('btn-admin').classList.add('active');
            document.getElementById('admin-tabs').style.display = 'flex';
            hidePanels();
            document.getElementById('tab-bronze').classList.add('active');
            initThreeJS();
        } else {
            alert("❌ Contraseña incorrecta. Acceso denegado.");
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

// VISOR ANATÓMICO 3D (THREE.JS)
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
initThreeJS();

// GRÁFICOS (CHART.JS)
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