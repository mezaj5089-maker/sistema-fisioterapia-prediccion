// Base de datos local
const rawPatients = [
  { id: 1, name: "Carlos Mendoza", diag: "Lumbalgia", zone: "Espalda Baja", sessions: 12, pred: "Alta en 3 semanas", status: "Alta Médica" },
  { id: 2, name: "María Torres", diag: "Tendinitis", zone: "Rodilla Derecha", sessions: 8, pred: "Alta en 1 semana", status: "En Tratamiento" },
  { id: 3, name: "Jorge Ramírez", diag: "Esguince", zone: "Tobillo Izquierdo", sessions: 5, pred: "Alta en 2 semanas", status: "En Tratamiento" },
  { id: 4, name: "Ana Delgado", diag: "Manguito", zone: "Hombro Derecho", sessions: 15, pred: "Alta en 4 semanas", status: "En Tratamiento" },
  { id: 5, name: "Luis Paredes", diag: "Lumbalgia", zone: "Espalda Baja", sessions: 10, pred: "Alta en 2 semanas", status: "Alta Médica" }
];

let trendChartInstance = null;

window.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  init3DViewer();
  initChart();
  applyFilters();
});

function applyFilters() {
  const searchVal = document.getElementById('searchPatient').value.toLowerCase();
  const diagVal = document.getElementById('filterDiag').value;

  const filtered = rawPatients.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(searchVal);
    const matchDiag = (diagVal === 'ALL') || p.diag === diagVal;
    return matchSearch && matchDiag;
  });

  renderTable(filtered);
  updateStats(filtered);
}

function resetFilters() {
  document.getElementById('searchPatient').value = '';
  document.getElementById('filterDiag').value = 'ALL';
  applyFilters();
}

function renderTable(patients) {
  const tbody = document.getElementById('patientTableBody');
  if (!tbody) return;

  if (patients.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-4 text-center text-slate-500">No se encontraron pacientes</td></tr>`;
    return;
  }

  tbody.innerHTML = patients.map(p => `
    <tr class="border-b border-slate-800/50 hover:bg-slate-800/30 transition">
      <td class="px-6 py-4 font-medium text-white">${p.name}</td>
      <td class="px-6 py-4">${p.diag}</td>
      <td class="px-6 py-4">${p.zone}</td>
      <td class="px-6 py-4">${p.sessions}</td>
      <td class="px-6 py-4 text-cyan-400 font-semibold">${p.pred}</td>
      <td class="px-6 py-4">
        <span class="px-2.5 py-1 text-xs rounded-full ${p.status === 'Alta Médica' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}">
          ${p.status}
        </span>
      </td>
    </tr>
  `).join('');
}

function updateStats(patients) {
  document.getElementById('statTotal').innerText = patients.length;
  const altas = patients.filter(p => p.status === 'Alta Médica').length;
  const rate = patients.length ? Math.round((altas / patients.length) * 100) : 0;
  document.getElementById('statRate').innerText = `${rate}%`;
  
  const totalSessions = patients.reduce((acc, p) => acc + p.sessions, 0);
  const avg = patients.length ? (totalSessions / patients.length).toFixed(1) : 0;
  document.getElementById('statAvg').innerText = avg;
}

function initChart() {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;

  trendChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5'],
      datasets: [
        { label: 'Lumbalgia', data: [12, 19, 15, 8, 4], borderColor: '#6366f1', tension: 0.3 },
        { label: 'Tendinitis', data: [8, 12, 18, 10, 5], borderColor: '#06b6d4', tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#94a3b8' } } },
      scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
        y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
      }
    }
  });
}

function init3DViewer() {
  const container = document.getElementById('canvas3d');
  if (!container) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const geometry = new THREE.CylinderGeometry(0.8, 0.6, 2.5, 16);
  const material = new THREE.MeshPhongMaterial({ color: 0x6366f1, wireframe: true });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(2, 2, 5).normalize();
  scene.add(light);

  camera.position.z = 4;

  function animate() {
    requestAnimationFrame(animate);
    mesh.rotation.y += 0.01;
    renderer.render(scene, camera);
  }
  animate();
}