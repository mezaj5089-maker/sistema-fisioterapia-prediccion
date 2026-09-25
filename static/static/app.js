// Carga inicial del panel
window.addEventListener('DOMContentLoaded', () => {
    console.log("Panel de Fisioterapia KineData inicializado.");
    initCharts();
    init3DViewer();
});

// Inicialización de Gráficos de Analítica
function initCharts() {
    const ctx = document.getElementById('analyticsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo', 'Abril'],
            datasets: [{
                label: 'Pacientes Atendidos',
                data: [12, 19, 15, 25],
                backgroundColor: '#0ea5e9'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            },
            scales: {
                x: { ticks: { color: '#f8fafc' } },
                y: { ticks: { color: '#f8fafc' } }
            }
        }
    });
}

// Inicialización del visor 3D para Anatomía/Músculos
function init3DViewer() {
    const container = document.getElementById('threeCanvas');
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.BoxGeometry(1, 2, 0.5);
    const material = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, wireframe: true });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    camera.position.z = 3;

    function animate() {
        requestAnimationFrame(animate);
        cube.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();
}