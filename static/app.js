// RELOJ DIGITAL DE PERÚ EN VIVO
function updateClock() {
    const now = new Date();
    const timeOptions = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const dateOptions = { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric' };
    
    const timeStr = now.toLocaleTimeString('es-PE', timeOptions);
    const dateStr = now.toLocaleDateString('es-PE', dateOptions);
    
    const relojElem = document.getElementById('reloj');
    if(relojElem) {
        relojElem.innerText = `${timeStr} - ${dateStr}`;
    }
}
setInterval(updateClock, 1000);
updateClock();

// CONMUTADOR ENTRE VISTA PACIENTE Y ADMIN
function setMode(mode) {
    document.getElementById('btn-paciente').classList.remove('active');
    document.getElementById('btn-admin').classList.remove('active');
    
    if(mode === 'paciente') {
        document.getElementById('btn-paciente').classList.add('active');
        document.getElementById('admin-tabs').style.display = 'none';
        hideAllPanels();
        document.getElementById('view-paciente-section').classList.add('active');
    } else {
        document.getElementById('btn-admin').classList.add('active');
        document.getElementById('admin-tabs').style.display = 'flex';
        hideAllPanels();
        document.getElementById('tab-bronze').classList.add('active');
        initThreeJS();
    }
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    hideAllPanels();
    document.getElementById(tabId).classList.add('active');
    
    if(tabId === 'tab-analytics') initCharts();
}

function hideAllPanels() {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
}

// BÚSQUEDA INTERACTIVA PACIENTE POR DNI
function buscarPaciente() {
    const dni = document.getElementById('dni-consulta').value;
    if(dni) {
        document.getElementById('resultado-paciente').style.display = 'block';
        document.getElementById('res-dni').innerText = dni;
    } else {
        alert("Por favor ingrese un DNI válido.");
    }
}

// VISOR ANATÓMICO 3D (THREE.JS)
function initThreeJS() {
    const container = document.getElementById('three-container');
    if(!container || container.children.length > 0) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.CylinderGeometry(0.8, 0.6, 2.5, 16);
    const material = new THREE.MeshBasicMaterial({ color: 0xa855f7, wireframe: true });
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

// GRÁFICOS ANALÍTICOS (CHART.JS)
let chartsLoaded = false;
function initCharts() {
    if(chartsLoaded) return;
    chartsLoaded = true;

    const ctxBar = document.getElementById('barChart');
    if(ctxBar) {
        new Chart(ctxBar.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Hombro', 'Rodilla', 'Lumbar', 'Cervical', 'Tobillo'],
                datasets: [{
                    label: 'Sesiones',
                    data: [16, 20, 14, 0, 0],
                    backgroundColor: '#06b6d4'
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }

    const ctxDonut = document.getElementById('donutChart');
    if(ctxDonut) {
        new Chart(ctxDonut.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Hombro', 'Rodilla', 'Lumbar'],
                datasets: [{
                    data: [1, 1, 1],
                    backgroundColor: ['#38bdf8', '#a855f7', '#ec4899']
                }]
            },
            options: { responsive: true }
        });
    }
}