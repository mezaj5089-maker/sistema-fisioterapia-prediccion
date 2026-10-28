let currentRol = 'paciente';
let currentDni = '72849102';

let pacientesData = [
    { dni: "72849102", nombre: "Juan Pérez", edad: 45, genero: "Masculino", zona: "Lumbar", eva_inicial: 8, tsk: 28, pcs: 22, sesiones_estimadas: 12, email: "juan.perez@gmail.com", tlf: "987654321" },
    { dni: "41920384", nombre: "María Rodríguez", edad: 32, genero: "Femenino", zona: "Cervical", eva_inicial: 5, tsk: 19, pcs: 15, sesiones_estimadas: 6, email: "maria.rod@gmail.com", tlf: "912345678" },
    { dni: "10823741", nombre: "Carlos Mendoza", edad: 58, genero: "Masculino", zona: "Rodilla", eva_inicial: 9, tsk: 34, pcs: 28, sesiones_estimadas: 15, email: "carlos.men@gmail.com", tlf: "998877665" }
];

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    renderTable(pacientesData);
    inicializarGraficos();
});

// Reloj oficial Perú UTC-5
function iniciarRelojPeru() {
    setInterval(() => {
        const ahora = new Date();
        const opcionesHora = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        const opcionesFecha = { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' };
        
        const rEl = document.getElementById("peru-clock");
        const fEl = document.getElementById("peru-date");
        if (rEl) rEl.innerText = ahora.toLocaleTimeString('es-PE', opcionesHora);
        if (fEl) fEl.innerText = ahora.toLocaleDateString('es-PE', opcionesFecha);
    }, 1000);
}

// Selección de Rol en Modal
function seleccionarRolModal(rol) {
    currentRol = rol;
    document.getElementById("btn-role-paciente").classList.toggle("active", rol === 'paciente');
    document.getElementById("btn-role-admin").classList.toggle("active", rol === 'admin');
    document.getElementById("group-pass").classList.toggle("hidden", rol === 'paciente');
}

// Iniciar Sesión por DNI
function iniciarSesion(e) {
    e.preventDefault();
    const dniInput = document.getElementById("login-dni").value.trim();
    if (!dniInput) return;

    currentDni = dniInput;
    document.getElementById("login-modal").classList.add("hidden");

    const badge = document.getElementById("badge-rol");
    badge.innerText = currentRol.toUpperCase();
    badge.className = `badge-role ${currentRol}`;

    if (currentRol === 'paciente') {
        document.getElementById("menu-paciente").classList.remove("hidden");
        document.getElementById("menu-admin").classList.add("hidden");
        switchTab('paciente-citas');
        
        // Buscar paciente en la base de datos simulada
        const pacienteEncontrado = pacientesData.find(p => String(p.dni).trim() === currentDni);
        if (pacienteEncontrado) {
            document.getElementById("p-dni-val").innerText = pacienteEncontrado.dni;
            document.getElementById("p-nombre-val").innerText = pacienteEncontrado.nombre;
            document.getElementById("p-dolencia-val").innerText = `${pacienteEncontrado.zona} (EVA: ${pacienteEncontrado.eva_inicial}/10)`;
            document.getElementById("p-sesiones-restantes").innerText = `Quedan ${pacienteEncontrado.sesiones_estimadas} Sesiones`;
            document.getElementById("user-display-name").innerText = `Paciente: ${pacienteEncontrado.nombre}`;
        } else {
            document.getElementById("p-dni-val").innerText = currentDni;
            document.getElementById("p-nombre-val").innerText = "Paciente Registrado (Nuevo)";
            document.getElementById("user-display-name").innerText = `DNI: ${currentDni}`;
        }
    } else {
        document.getElementById("menu-paciente").classList.add("hidden");
        document.getElementById("menu-admin").classList.remove("hidden");
        switchTab('admin-registro');
        document.getElementById("user-display-name").innerText = "Administrador / Fisioterapeuta Principal";
    }
}

function cerrarSesion() {
    document.getElementById("login-modal").classList.remove("hidden");
}

// Navegación de Vistas
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
    
    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');
}

// Solicitud de Reprogramación (Paciente)
function enviarSolicitudReprogramacion(e) {
    e.preventDefault();
    const fecha = document.getElementById("rep-fecha").value;
    const hora = document.getElementById("rep-hora").value;
    const motivo = document.getElementById("rep-motivo").value;

    const statusBox = document.getElementById("status-reprogramacion");
    statusBox.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-circle-check text-green"></i> <strong>Solicitud enviada con éxito.</strong><br>
            Fecha propuesta: <strong>${fecha} a las ${hora}</strong>.<br>
            Estado: <span class="text-cyan">Pendiente de aprobación administrativa. Se le notificará a su correo.</span>
        </div>
    `;
}

// Registro Admin y Predicción ML
function registrarPacienteAdmin() {
    const dni = document.getElementById("adm_dni").value.trim();
    const nombre = document.getElementById("adm_nombre").value;
    const edad = parseInt(document.getElementById("adm_edad").value);
    const genero = document.getElementById("adm_genero").value;
    const zona = document.getElementById("adm_zona").value;
    const eva = parseInt(document.getElementById("adm_eva").value);
    const tsk = parseInt(document.getElementById("adm_tsk").value);
    const pcs = parseInt(document.getElementById("adm_pcs").value);
    const dias = parseInt(document.getElementById("adm_dias").value);
    const email = document.getElementById("adm_email").value;
    const tlf = document.getElementById("adm_tlf").value;

    // Cálculo predictivo con Random Forest (simulado)
    const sesionesEst = Math.round((eva * 0.75) + (tsk * 0.12) + (pcs * 0.1) + (edad * 0.03));

    const nuevo = {
        dni: dni,
        nombre: nombre,
        edad: edad,
        genero: genero,
        zona: zona,
        eva_inicial: eva,
        tsk: tsk,
        pcs: pcs,
        sesiones_estimadas: sesionesEst > 0 ? sesionesEst : 8,
        email: email,
        tlf: tlf
    };

    pacientesData.unshift(nuevo);
    renderTable(pacientesData);

    const box = document.getElementById("result-ia-panel");
    const txt = document.getElementById("result-text");
    if (txt) {
        txt.innerHTML = `Paciente <strong>${nombre}</strong> procesado correctamente (Bronze -> Silver).<br>Proyección óptima del Modelo IA: <span class="text-cyan">${nuevo.sesiones_estimadas} sesiones de rehabilitación</span> (Probabilidad de Éxito: 91.4%).`;
    }
    if (box) box.classList.remove("hidden");
}

// Renderizado de Capa Silver en Tabla
function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    data.forEach(p => {
        tbody.innerHTML += `
            <tr>
                <td><strong>${p.dni}</strong></td>
                <td>${p.nombre}<br><small class="text-muted">${p.email || 'Sin correo'} / ${p.tlf || ''}</small></td>
                <td class="text-cyan">${p.zona}</td>
                <td>${p.eva_inicial}/10 | ${p.tsk} / ${p.pcs}</td>
                <td>Activo (Capa Silver)</td>
                <td><strong class="text-green">${p.sesiones_estimadas} ses.</strong></td>
                <td><button class="btn-success" onclick="alert('Historial clínico verificado.')">Ver</button></td>
            </tr>
        `;
    });
}

// Filtrar Pacientes por DNI o Nombre
function filterPatients() {
    const q = document.getElementById('searchDni').value.toLowerCase().trim();
    const filtrados = pacientesData.filter(p => 
        String(p.dni).toLowerCase().includes(q) || 
        String(p.nombre).toLowerCase().includes(q)
    );
    renderTable(filtrados);
}

// Enviar Notificación por Gmail o SMS
function enviarNotificacionPaciente(e) {
    e.preventDefault();
    const canal = document.getElementById("notif-canal").value;
    const mensaje = document.getElementById("notif-mensaje").value;

    const box = document.getElementById("status-envio-notif");
    box.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-paper-plane text-cyan"></i> <strong>Notificación enviada exitosamente.</strong><br>
            Canal utilizado: <strong>${canal}</strong>.<br>
            El paciente ha sido informado correctamente en su bandeja y celular.
        </div>
    `;
}

// Exportar a Excel con SheetJS
function exportToExcel() {
    const ws = XLSX.utils.json_to_sheet(pacientesData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Capa_Silver_Pacientes");
    XLSX.writeFile(wb, "KineData_Reporte_Silver.xlsx");
}

// Gráficos Chart.js
function inicializarGraficos() {
    const ctxL = document.getElementById('chartLesiones');
    if (ctxL) {
        new Chart(ctxL.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Lumbar', 'Cervical', 'Hombro', 'Rodilla', 'Tobillo'],
                datasets: [{ data: [450, 280, 210, 160, 100], backgroundColor: '#38bdf8' }]
            },
            options: { plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
        });
    }

    const ctxA = document.getElementById('chartAdherencia');
    if (ctxA) {
        new Chart(ctxA.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Éxito Favorable', 'En Evolución', 'Riesgo Deserción'],
                datasets: [{ data: [82, 12, 6], backgroundColor: ['#34d399', '#38bdf8', '#f59e0b'] }]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#f8fafc', boxWidth: 12 } } } }
        });
    }
}