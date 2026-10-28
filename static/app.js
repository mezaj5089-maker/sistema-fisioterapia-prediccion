let currentRol = 'paciente';
let currentDni = '72849102';

let pacientesData = [
    {
        dni: "72849102",
        nombre: "Juan Pérez",
        edad: 45,
        zona: "Lumbar",
        eva: 7,
        fecha_inicio: "2026-10-15",
        sesiones_totales: 10,
        sesiones_restantes: 8,
        email: "juan.perez@gmail.com",
        tlf: "987654321",
        tutor: "María Pérez (Esposa)",
        tutor_tlf: "912345678",
        horario: "09:00 AM - 10:00 AM"
    },
    {
        dni: "41920384",
        nombre: "Carlos Mendoza",
        edad: 32,
        zona: "Cervical",
        eva: 5,
        fecha_inicio: "2026-10-18",
        sesiones_totales: 12,
        sesiones_restantes: 2,
        email: "carlos.mendoza@gmail.com",
        tlf: "998877665",
        tutor: "Jorge Mendoza (Padre)",
        tutor_tlf: "955443322",
        horario: "11:00 AM - 12:00 PM"
    }
];

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    renderTable(pacientesData);
    poblardeSelectNotificaciones();
    inicializarGraficos();
});

// Reloj Digital Perú UTC-5
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

function seleccionarRolModal(rol) {
    currentRol = rol;
    document.getElementById("btn-role-paciente").classList.toggle("active", rol === 'paciente');
    document.getElementById("btn-role-admin").classList.toggle("active", rol === 'admin');
    document.getElementById("group-pass").classList.toggle("hidden", rol === 'paciente');
}

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
        
        const paciente = pacientesData.find(p => String(p.dni).trim() === currentDni) || pacientesData[0];
        document.getElementById("p-dni-val").innerText = paciente.dni;
        document.getElementById("p-nombre-val").innerText = paciente.nombre;
        document.getElementById("p-dolencia-val").innerText = `${paciente.zona} (EVA: ${paciente.eva}/10)`;
        document.getElementById("p-fecha-inicio").innerText = paciente.fecha_inicio;
        document.getElementById("p-tutor-val").innerText = `${paciente.tutor} (${paciente.tutor_tlf})`;
        
        document.getElementById("p-sesiones-restantes").innerText = paciente.sesiones_restantes;
        document.getElementById("p-sesiones-totales").innerText = paciente.sesiones_totales;

        const alertBox = document.getElementById("alert-mantenimiento");
        if (paciente.sesiones_restantes <= 2) {
            alertBox.classList.remove("hidden");
        } else {
            alertBox.classList.add("hidden");
        }
        document.getElementById("user-display-name").innerText = `Paciente: ${paciente.nombre}`;
    } else {
        document.getElementById("menu-paciente").classList.add("hidden");
        document.getElementById("menu-admin").classList.remove("hidden");
        switchTab('admin-registro');
        document.getElementById("user-display-name").innerText = "Fisioterapeuta / Administrador de Clínica";
    }
}

function cerrarSesion() {
    document.getElementById("login-modal").classList.remove("hidden");
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
    
    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');
}

// Reprogramación de Paciente
function enviarSolicitudReprogramacion(e) {
    e.preventDefault();
    const fecha = document.getElementById("rep-fecha").value;
    const hora = document.getElementById("rep-hora").value;

    const statusBox = document.getElementById("status-reprogramacion");
    statusBox.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-circle-check text-green"></i> <strong>Solicitud recibida.</strong><br>
            Su propuesta para el <strong>${fecha} a las ${hora}</strong> está en revisión médica. Se notificará a su correo y al teléfono de su tutor.
        </div>
    `;
}

// Registro Completo en Admin
function registrarPacienteAdmin() {
    const dni = document.getElementById("adm_dni").value.trim();
    const nombre = document.getElementById("adm_nombre").value;
    const edad = parseInt(document.getElementById("adm_edad").value);
    const email = document.getElementById("adm_email").value;
    const tlf = document.getElementById("adm_tlf").value;
    const tutor = document.getElementById("adm_tutor").value;
    const tutor_tlf = document.getElementById("adm_tutor_tlf").value;
    const zona = document.getElementById("adm_zona").value;
    const eva = parseInt(document.getElementById("adm_eva").value);
    const fecha_inicio = document.getElementById("adm_fecha_inicio").value;
    const sesiones_recetadas = parseInt(document.getElementById("adm_sesiones_recetadas").value);
    const horario = document.getElementById("adm_horario").value;

    const nuevo = {
        dni, nombre, edad, zona, eva,
        fecha_inicio: fecha_inicio || "2026-10-28",
        sesiones_totales: sesiones_recetadas,
        sesiones_restantes: sesiones_recetadas,
        email, tlf, tutor, tutor_tlf, horario
    };

    pacientesData.unshift(nuevo);
    renderTable(pacientesData);
    poblardeSelectNotificaciones();

    const box = document.getElementById("result-ia-panel");
    const txt = document.getElementById("result-text");
    txt.innerHTML = `Paciente <strong>${nombre}</strong> y Tutor <strong>${tutor}</strong> registrados con éxito.<br>Inferencia de IA: Proyección de cumplimiento óptimo del 89.2% en ${sesiones_recetadas} sesiones.`;
    box.classList.remove("hidden");
}

// Renderizado de Tabla Silver + Botón Descontar Sesión
function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    data.forEach((p, index) => {
        const esAlerta = p.sesiones_restantes <= 2;
        const estadoPill = esAlerta 
            ? `<span class="status-pill warn"><i class="fa-solid fa-triangle-exclamation"></i> Mantenimiento / Extensión</span>`
            : `<span class="status-pill good">En Tratamiento Normal</span>`;

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.dni}</strong></td>
                <td>
                    <strong>${p.nombre}</strong><br>
                    <small class="text-muted">Tutor: ${p.tutor} (${p.tutor_tlf})</small>
                </td>
                <td><strong class="text-primary">${p.zona}</strong> (EVA: ${p.eva}/10)</td>
                <td>${p.fecha_inicio}</td>
                <td><strong class="highlight-text">${p.sesiones_restantes}</strong> / ${p.sesiones_totales} ses.</td>
                <td>${estadoPill}</td>
                <td>
                    <button class="btn-action-small" onclick="marcarAsistencia(${index})">
                        <i class="fa-solid fa-check"></i> Asistió (-1 Sesión)
                    </button>
                </td>
            </tr>
        `;
    });
}

// Marcar Asistencia y Descontar Contador
function marcarAsistencia(index) {
    if (pacientesData[index].sesiones_restantes > 0) {
        pacientesData[index].sesiones_restantes -= 1;
        renderTable(pacientesData);

        if (pacientesData[index].sesiones_restantes <= 2) {
            alert(`⚠️ Alerta Médica: Al paciente ${pacientesData[index].nombre} le quedan ${pacientesData[index].sesiones_restantes} sesiones. Se sugiere evaluar adición de más sesiones o terapia de relajación/mantenimiento.`);
        } else {
            alert(`✅ Asistencia registrada correctamente. Le quedan ${pacientesData[index].sesiones_restantes} sesiones.`);
        }
    } else {
        alert(`ℹ️ El paciente ya culminó las sesiones asignadas.`);
    }
}

function filterPatients() {
    const q = document.getElementById('searchDni').value.toLowerCase().trim();
    const filtrados = pacientesData.filter(p => 
        String(p.dni).toLowerCase().includes(q) || 
        String(p.nombre).toLowerCase().includes(q)
    );
    renderTable(filtrados);
}

function poblardeSelectNotificaciones() {
    const select = document.getElementById("notif-paciente-select");
    if (!select) return;
    select.innerHTML = '';
    pacientesData.forEach(p => {
        select.innerHTML += `<option value="${p.dni}">${p.nombre} - Tutor: ${p.tutor}</option>`;
    });
}

function enviarNotificacionPaciente(e) {
    e.preventDefault();
    const canal = document.getElementById("notif-canal").value;
    const box = document.getElementById("status-envio-notif");
    box.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-paper-plane text-primary"></i> <strong>Notificación emitida por ${canal}.</strong><br>
            Se ha enviado el aviso tanto al paciente como a su tutor/familiar registrado.
        </div>
    `;
}

function exportToExcel() {
    const ws = XLSX.utils.json_to_sheet(pacientesData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Expedientes_Silver");
    XLSX.writeFile(wb, "Reporte_Clinico_Fisioterapia.xlsx");
}

function inicializarGraficos() {
    const ctxL = document.getElementById('chartLesiones');
    if (ctxL) {
        new Chart(ctxL.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Lumbar', 'Cervical', 'Hombro', 'Rodilla', 'Tobillo'],
                datasets: [{ data: [420, 290, 210, 150, 110], backgroundColor: '#0284c7' }]
            },
            options: { plugins: { legend: { display: false } } }
        });
    }

    const ctxA = document.getElementById('chartAdherencia');
    if (ctxA) {
        new Chart(ctxA.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Recuperación Completa', 'En Mantenimiento', 'Pendientes'],
                datasets: [{ data: [80, 15, 5], backgroundColor: ['#10b981', '#0284c7', '#f59e0b'] }]
            },
            options: { plugins: { legend: { position: 'bottom' } } }
        });
    }
}