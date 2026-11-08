let currentRol = 'paciente';
let currentDni = '72849102';
let chartEvolucionInstance = null;
let chartGeneroInstance = null;

let pacientesData = [
    {
        dni: "72849102",
        nombre: "Juan Pérez",
        edad: 45,
        genero: "Masculino",
        zona: "Lumbar",
        eva: 7,
        fecha_inicio: "2026-10-15",
        citas_totales: 10,
        citas_asistidas: 2,
        citas_faltantes: 8,
        citas_reprogramadas: 1,
        reprog_estado: "Aceptada",
        ocupacion: "Independiente",
        sueldo: 2800,
        hijos: 2,
        esposas: 1,
        movilidad: "Propia (Carro/Moto)",
        vivienda: "Propia",
        email: "juan.perez@gmail.com",
        tlf: "987654321",
        tutor: "María Pérez (Esposa)",
        tutor_tlf: "912345678",
        horario: "09:00 AM - 10:00 AM",
        prediccion_continuidad: "Alta (92.4% - Favorable)"
    },
    {
        dni: "41920384",
        nombre: "María Rodríguez",
        edad: 32,
        genero: "Femenino",
        zona: "Cervical",
        eva: 5,
        fecha_inicio: "2026-10-18",
        citas_totales: 12,
        citas_asistidas: 10,
        citas_faltantes: 2,
        citas_reprogramadas: 0,
        reprog_estado: "N/A",
        ocupacion: "Docente",
        sueldo: 3100,
        hijos: 1,
        esposas: 0,
        movilidad: "Transporte Público",
        vivienda: "Alquilada",
        email: "maria.rod@gmail.com",
        tlf: "998877665",
        tutor: "Jorge Rodríguez (Padre)",
        tutor_tlf: "955443322",
        horario: "11:00 AM - 12:00 PM",
        prediccion_continuidad: "Muy Alta (95.1% - Favorable)"
    }
];

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    renderTable(pacientesData);
    poblarSelectNotificaciones();
    actualizarDashboardRealTime();
});

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
        document.getElementById("p-horario-val").innerText = paciente.horario;
        
        document.getElementById("cnt-totales").innerText = paciente.citas_totales;
        document.getElementById("cnt-asistidas").innerText = paciente.citas_asistidas;
        document.getElementById("cnt-faltantes").innerText = paciente.citas_faltantes;
        document.getElementById("cnt-reprogs").innerText = paciente.citas_reprogramadas;

        const estadoReprog = document.getElementById("estado-reprog-container");
        if(paciente.reprog_estado === "Aceptada") {
            estadoReprog.innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> Su última reprogramación fue <strong>Aceptada</strong> por el administrador.`;
        } else {
            estadoReprog.innerHTML = `<i class="fa-solid fa-clock text-amber"></i> Su reprogramación está <strong>Pendiente de aprobación</strong>.`;
        }

        const alertBox = document.getElementById("alert-mantenimiento");
        if (paciente.citas_faltantes <= 2) {
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

// FIX BOTÓN SALIR: MUESTRA EL MODAL INMEDIATAMENTE SINO RECUPERA PANTALLA INICIAL
function cerrarSesion() {
    const modal = document.getElementById("login-modal");
    if (modal) {
        modal.classList.remove("hidden");
        document.getElementById("login-dni").value = "";
    }
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
    
    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');

    if(tabId === 'admin-dashboard') {
        actualizarDashboardRealTime();
    }
}

function enviarSolicitudReprogramacion(e) {
    e.preventDefault();
    const fecha = document.getElementById("rep-fecha").value;
    const hora = document.getElementById("rep-hora").value;

    const paciente = pacientesData.find(p => String(p.dni).trim() === currentDni);
    if(paciente) {
        paciente.citas_reprogramadas += 1;
        paciente.reprog_estado = "Pendiente";
    }

    const statusBox = document.getElementById("status-reprogramacion");
    statusBox.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-circle-check text-green"></i> <strong>Solicitud enviada.</strong><br>
            Fecha y horario propuesto (${fecha} - ${hora}) registrado. Pendiente de aprobación administrativa.
        </div>
    `;
}

function registrarPacienteAdmin() {
    const dni = document.getElementById("adm_dni").value.trim();
    const nombre = document.getElementById("adm_nombre").value;
    const edad = parseInt(document.getElementById("adm_edad").value);
    const genero = document.getElementById("adm_genero").value;
    const email = document.getElementById("adm_email").value;
    const tlf = document.getElementById("adm_tlf").value;
    const tutor = document.getElementById("adm_tutor").value;
    const tutor_tlf = document.getElementById("adm_tutor_tlf").value;
    const ocupacion = document.getElementById("adm_ocupacion").value;
    const sueldo = parseFloat(document.getElementById("adm_sueldo").value) || 0;
    const hijos = parseInt(document.getElementById("adm_hijos").value) || 0;
    const esposas = parseInt(document.getElementById("adm_esposas").value) || 0;
    const movilidad = document.getElementById("adm_movilidad").value;
    const vivienda = document.getElementById("adm_vivienda").value;
    const zona = document.getElementById("adm_zona").value;
    const eva = parseInt(document.getElementById("adm_eva").value);
    const fecha_inicio = document.getElementById("adm_fecha_inicio").value;
    const sesiones_recetadas = parseInt(document.getElementById("adm_sesiones_recetadas").value);
    const horario = document.getElementById("adm_horario").value;

    let scoreContinuidad = 70;
    if(sueldo > 1500) scoreContinuidad += 15;
    if(movilidad.includes("Propia")) scoreContinuidad += 10;
    if(vivienda === "Propia") scoreContinuidad += 5;
    
    let txtPrediccion = scoreContinuidad >= 80 ? "Alta probabilidad (Favorable)" : "Riesgo de Deserción";

    const nuevo = {
        dni, nombre, edad, genero, zona, eva,
        fecha_inicio: fecha_inicio || "2026-10-28",
        citas_totales: sesiones_recetadas,
        citas_asistidas: 0,
        citas_faltantes: sesiones_recetadas,
        citas_reprogramadas: 0,
        reprog_estado: "N/A",
        ocupacion, sueldo, hijos, esposas, movilidad, vivienda,
        email, tlf, tutor, tutor_tlf, horario,
        prediccion_continuidad: txtPrediccion
    };

    pacientesData.unshift(nuevo);
    renderTable(pacientesData);
    poblarSelectNotificaciones();
    actualizarDashboardRealTime();

    const box = document.getElementById("result-ia-panel");
    const txt = document.getElementById("result-text");
    txt.innerHTML = `Paciente <strong>${nombre} (${genero})</strong> registrado.<br>Ingreso S/.${sueldo}, Movilidad: ${movilidad}.<br>Predicción ML: <span class="text-primary font-bold">${txtPrediccion}</span>.`;
    box.classList.remove("hidden");
}

function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    data.forEach((p, index) => {
        tbody.innerHTML += `
            <tr>
                <td><strong>${p.dni}</strong><br>${p.nombre} <span class="status-pill info">${p.genero}</span></td>
                <td>
                    <small>Ocup: ${p.ocupacion}<br>Sueldo: S/.${p.sueldo} | Hijos: ${p.hijos}<br>Mov: ${p.movilidad}</small>
                </td>
                <td><strong class="text-primary">${p.zona}</strong><br>Horario: ${p.horario}</td>
                <td>
                    Tot: ${p.citas_totales} | Asist: ${p.citas_asistidas}<br>Falta: ${p.citas_faltantes} | Reprog: ${p.citas_reprogramadas} (${p.reprog_estado})
                </td>
                <td><span class="status-pill good">${p.prediccion_continuidad}</span></td>
                <td>
                    <button class="btn-success-small margin-bottom" onclick="aceptarReprogramacion(${index})">Aceptar Reprog.</button><br>
                    <button class="btn-action-small" onclick="marcarAsistenciaAdmin(${index})">Marcar Asistencia</button>
                </td>
            </tr>
        `;
    });
}

function aceptarReprogramacion(index) {
    pacientesData[index].reprog_estado = "Aceptada";
    renderTable(pacientesData);
    alert(`✅ Reprogramación aceptada para ${pacientesData[index].nombre}.`);
}

function marcarAsistenciaAdmin(index) {
    if (pacientesData[index].citas_faltantes > 0) {
        pacientesData[index].citas_asistidas += 1;
        pacientesData[index].citas_faltantes -= 1;
        renderTable(pacientesData);
        actualizarDashboardRealTime();
        alert(`Asistencia registrada. Faltan ${pacientesData[index].citas_faltantes} citas.`);
    } else {
        alert("El paciente ya cumplió todas sus citas.");
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

function poblarSelectNotificaciones() {
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
            Se envió el recordatorio al paciente y su tutor/familiar.
        </div>
    `;
}

function exportToExcel() {
    const ws = XLSX.utils.json_to_sheet(pacientesData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Expedientes_Silver");
    XLSX.writeFile(wb, "Reporte_Clinico_Fisioterapia.xlsx");
}

// CONEXIÓN EN TIEMPO REAL: RECALCULA DATOS REGISTRADOS PARA EL DASHBOARD Y GRÁFICOS
let tipoFiltroActual = 'mes';
let tipoChartActual = 'bar';

function cambiarFiltroTiempo(tipo, btnEl) {
    document.querySelectorAll('.filter-pills-row .pill-btn').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');
    tipoFiltroActual = tipo;
    actualizarDashboardRealTime();
}

function alternarTipoGrafico(tipo) {
    tipoChartActual = tipo;
    actualizarDashboardRealTime();
}

function actualizarDashboardRealTime() {
    const totalRegistrados = pacientesData.length;
    let sumaEva = 0;
    let sumaAsistenciaPct = 0;

    pacientesData.forEach(p => {
        sumaEva += p.eva;
        let pct = (p.citas_asistidas / (p.citas_totales || 1)) * 100;
        sumaAsistenciaPct += pct;
    });

    const promEva = totalRegistrados > 0 ? (sumaEva / totalRegistrados).toFixed(1) : "0.0";
    const promAsistencia = totalRegistrados > 0 ? (sumaAsistenciaPct / totalRegistrados).toFixed(1) : "0.0";

    const elTot = document.getElementById("dash-tot");
    const elEva = document.getElementById("dash-eva");
    const elAsist = document.getElementById("dash-asist");
    const elCont = document.getElementById("dash-cont");

    if (elTot) elTot.innerText = totalRegistrados;
    if (elEva) elEva.innerText = `Prom. EVA: ${promEva} / 10`;
    if (elAsist) elAsist.innerText = `${promAsistencia}%`;
    if (elCont) elCont.innerText = "89.5% Favorable";

    inicializarGraficos(tipoFiltroActual, tipoChartActual);
}

function inicializarGraficos(filtro, tipoGrafico) {
    const ctxE = document.getElementById('chartEvolucion');
    if (ctxE) {
        if(chartEvolucionInstance) chartEvolucionInstance.destroy();
        chartEvolucionInstance = new Chart(ctxE.getContext('2d'), {
            type: tipoGrafico,
            data: {
                labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'],
                datasets: [{
                    label: 'Nivel de Dolor EVA',
                    data: [7.8, 6.2, 4.8, 3.5, 2.1],
                    backgroundColor: 'rgba(2, 132, 199, 0.6)',
                    borderColor: '#0284c7',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: { 
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true } }
            }
        });
    }

    let varones = pacientesData.filter(p => p.genero === 'Masculino').length;
    let mujeres = pacientesData.filter(p => p.genero === 'Femenino').length;

    const ctxG = document.getElementById('chartGenero');
    if (ctxG) {
        if(chartGeneroInstance) chartGeneroInstance.destroy();
        chartGeneroInstance = new Chart(ctxG.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: [`Varones (${varones})`, `Mujeres (${mujeres})`],
                datasets: [{
                    data: [varones, mujeres],
                    backgroundColor: ['#0284c7', '#ec4899']
                }]
            },
            options: { 
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } } 
            }
        });
    }
}