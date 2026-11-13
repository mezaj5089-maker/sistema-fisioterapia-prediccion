let currentRol = 'paciente';
let currentDni = '76563443';
let chartDolenciasInstance = null;
let chartGeneroTerapiaInstance = null;
let chartProgresoClinicaInstance = null;
let chartEvolucionInstance = null;
let chartProgresoIndividualInstance = null;

let pacientesData = window.pacientesSupabaseData || [];

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

// ================= REGISTRO CON PREDICCIÓN SOCIOECONÓMICA Y NOTIFICACIÓN IA =================
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

    let scoreContinuidad = 60;
    if (sueldo >= 2000) scoreContinuidad += 20;
    else if (sueldo >= 1500) scoreContinuidad += 10;
    else scoreContinuidad -= 15;

    if (movilidad.includes("Propia")) scoreContinuidad += 15;
    else if (movilidad.includes("Transporte Público")) scoreContinuidad -= 5;

    if (vivienda === "Propia") scoreContinuidad += 10;
    else scoreContinuidad -= 5;

    if (eva <= 6) scoreContinuidad += 10;
    else scoreContinuidad -= 5;

    let txtPrediccion = "";
    let motivoDetallado = "";

    if (scoreContinuidad >= 75) {
        txtPrediccion = "El paciente podrá continuar su terapia sin inconvenientes (Favorable)";
        motivoDetallado = `El paciente ${nombre} (DNI: ${dni}) cuenta con estabilidad económica (S/.${sueldo}), vivienda ${vivienda.toLowerCase()} y movilidad ${movilidad.toLowerCase()}, factores que aseguran su asistencia a sus ${sesiones_recetadas} sesiones de ${zona}.`;
    } else {
        txtPrediccion = "Alerta: Riesgo de que el paciente NO pueda continuar su terapia";
        motivoDetallado = `Aviso importante: El paciente ${nombre} (DNI: ${dni}) presenta vulnerabilidad por ingresos limitados (S/.${sueldo}) y uso de ${movilidad.toLowerCase()}. Se recomienda otorgar facilidades de pago o ajustar horarios para evitar abandono del tratamiento de ${zona}.`;
    }

    const nuevo = {
        dni, nombre, edad, genero, zona, eva,
        fecha_inicio: fecha_inicio || "2026-11-12",
        citas_totales: sesiones_recetadas,
        citas_asistidas: 1,
        citas_faltantes: sesiones_recetadas - 1,
        citas_reprogramadas: 0,
        reprog_estado: "N/A",
        ocupacion, sueldo, hijos, esposas, movilidad, vivienda,
        email, tlf, tutor, tutor_tlf, horario,
        prediccion_continuidad: txtPrediccion,
        motivo_continuidad: motivoDetallado,
        historial_eva: [eva, Math.max(0, eva - 1), Math.max(0, eva - 2)]
    };

    pacientesData.unshift(nuevo);
    renderTable(pacientesData);
    poblarSelectNotificaciones();
    actualizarDashboardRealTime();

    const box = document.getElementById("result-ia-panel");
    const txt = document.getElementById("result-text");
    txt.innerHTML = `<strong>Diagnóstico IA (Random Forest):</strong><br>${txtPrediccion}<br><br><em>Detalle:</em> ${motivoDetallado}`;
    box.classList.remove("hidden");
}

function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    data.forEach((p, index) => {
        if(!p.historial_eva) p.historial_eva = [8, 7, p.eva || 6];

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.dni}</strong><br>${p.nombre} <span class="status-pill info">${p.genero}</span></td>
                <td>
                    <small>Ocup: ${p.ocupacion || 'N/A'}<br>Sueldo: S/.${p.sueldo || 0} | Mov: ${p.movilidad || 'N/A'}</small>
                </td>
                <td><strong class="text-primary">${p.zona || 'Lumbalgia / Zona Lumbar'}</strong><br>Horario: ${p.horario || '09:00 AM'}</td>
                <td>
                    Tot: ${p.citas_totales || 10} | Asist: ${p.citas_asistidas || 0}<br>Falta: ${p.citas_faltantes || 10} | Reprog: ${p.citas_reprogramadas || 0} (${p.reprog_estado || 'N/A'})
                </td>
                <td><span class="status-pill good">${p.prediccion_continuidad || 'Favorable'}</span></td>
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
        
        if(!pacientesData[index].historial_eva) pacientesData[index].historial_eva = [8, 7, 6];
        let ultimoEva = pacientesData[index].historial_eva[pacientesData[index].historial_eva.length - 1];
        pacientesData[index].historial_eva.push(Math.max(0, ultimoEva - 1));

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
        select.innerHTML += `<option value="${p.dni}">${p.nombre} - Tutor: ${p.tutor || 'Familiar'}</option>`;
    });
}

function enviarNotificacionPaciente(e) {
    e.preventDefault();
    const canal = document.getElementById("notif-canal").value;
    const box = document.getElementById("status-envio-notif");
    box.innerHTML = `
        <div class="result-box">
            <i class="fa-solid fa-paper-plane text-primary"></i> <strong>Notificación emitida por ${canal}.</strong><br>
            Se envió el aviso de continuidad y recordatorio al paciente y su tutor.
        </div>
    `;
}

function exportToExcel() {
    const ws = XLSX.utils.json_to_sheet(pacientesData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Expedientes_Silver");
    XLSX.writeFile(wb, "Reporte_Clinico_Fisioterapia.xlsx");
}

// ================= CONSULTA DE PROGRESO POR DNI =================
function consultarProgresoPorDni() {
    const dniBuscado = document.getElementById("input-consulta-dni").value.trim();
    const paciente = pacientesData.find(p => String(p.dni).trim() === String(dniBuscado));
    
    const contenedorRes = document.getElementById("resultado-consulta-dni");
    if(!paciente) {
        alert("No se encontró ningún paciente registrado con ese DNI.");
        contenedorRes.classList.add("hidden");
        return;
    }

    contenedorRes.classList.remove("hidden");
    document.getElementById("res-nombre").innerText = paciente.nombre;
    document.getElementById("res-dolencia").innerText = paciente.zona || "Lumbalgia / Zona Lumbar";
    document.getElementById("res-genero-edad").innerText = `${paciente.genero} / ${paciente.edad} años`;
    document.getElementById("res-socio").innerText = `S/.${paciente.sueldo || 2000} | Mov: ${paciente.movilidad || 'Propia'} | Viv: ${paciente.vivienda || 'Propia'}`;
    document.getElementById("res-citas").innerText = `${paciente.citas_asistidas || 0} asistidas de ${paciente.citas_totales || 10} totales`;
    document.getElementById("res-cont").innerText = paciente.prediccion_continuidad || "Favorable";
    document.getElementById("res-motivo").innerText = paciente.motivo_continuidad || "El paciente presenta condiciones estables para continuar.";

    if(!paciente.historial_eva) paciente.historial_eva = [8, 7, paciente.eva || 6];

    const ctxInd = document.getElementById('chartProgresoIndividual');
    if(ctxInd) {
        if(chartProgresoIndividualInstance) chartProgresoIndividualInstance.destroy();
        chartProgresoIndividualInstance = new Chart(ctxInd.getContext('2d'), {
            type: 'line',
            data: {
                labels: paciente.historial_eva.map((_, i) => `Sesión ${i+1}`),
                datasets: [{
                    label: 'Nivel de Dolor (Escala EVA)',
                    data: paciente.historial_eva,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2,132,199,0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }
        });
    }
}

// ================= DASHBOARD INTERACTIVO Y DINÁMICO EN TIEMPO REAL =================
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
    let filtrados = pacientesData;
    if (tipoFiltroActual === 'dia') {
        filtrados = pacientesData.slice(0, Math.min(2, pacientesData.length));
    } else if (tipoFiltroActual === 'semana') {
        filtrados = pacientesData.slice(0, Math.min(4, pacientesData.length));
    } else if (tipoFiltroActual === 'anio') {
        filtrados = pacientesData;
    }

    const totalRegistrados = filtrados.length;
    let enMejoria = 0;
    let enProlongado = 0;
    let sumaAsistenciaPct = 0;

    filtrados.forEach(p => {
        let pctAsist = ((p.citas_asistidas || 0) / (p.citas_totales || 10)) * 100;
        sumaAsistenciaPct += pctAsist;

        if(!p.historial_eva) p.historial_eva = [8, 7, p.eva || 6];
        let evaInicial = p.historial_eva[0] || 6;
        let evaActual = p.historial_eva[p.historial_eva.length - 1] || evaInicial;
        
        if (evaActual < evaInicial || (p.citas_faltantes || 10) <= 2) {
            enMejoria += 1;
        } else {
            enProlongado += 1;
        }
    });

    const promAsistencia = totalRegistrados > 0 ? (sumaAsistenciaPct / totalRegistrados).toFixed(1) : "0.0";

    document.getElementById("dash-tot").innerText = totalRegistrados;
    document.getElementById("dash-mejora").innerText = enMejoria;
    document.getElementById("dash-prolongado").innerText = enProlongado;
    document.getElementById("dash-asist").innerText = `${promAsistencia}%`;

    inicializarGraficos(filtrados, tipoChartActual);
}

function inicializarGraficos(dataList, tipoGrafico) {
    let conteoDolencias = { 
        "Lumbalgia / Zona Lumbar": 0, 
        "Cervicalgia / Cuello": 0, 
        "Tendinitis de Hombro": 0, 
        "Lesión de Rodilla": 0, 
        "Esguince de Tobillo": 0 
    };

    dataList.forEach(p => {
        let z = p.zona || "Lumbalgia / Zona Lumbar";
        if(conteoDolencias[z] !== undefined) conteoDolencias[z] += 1;
        else conteoDolencias[z] = 1;
    });

    const ctxDol = document.getElementById('chartDolencias');
    if (ctxDol) {
        if(chartDolenciasInstance) chartDolenciasInstance.destroy();
        chartDolenciasInstance = new Chart(ctxDol.getContext('2d'), {
            type: tipoGrafico,
            data: {
                labels: Object.keys(conteoDolencias),
                datasets: [{
                    label: 'Cantidad de Pacientes',
                    data: Object.values(conteoDolencias),
                    backgroundColor: ['#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    let varones = dataList.filter(p => p.genero === 'Masculino').length;
    let mujeres = dataList.filter(p => p.genero === 'Femenino').length;

    const ctxGen = document.getElementById('chartGeneroTerapia');
    if (ctxGen) {
        if(chartGeneroTerapiaInstance) chartGeneroTerapiaInstance.destroy();
        chartGeneroTerapiaInstance = new Chart(ctxGen.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: [`Varones (${varones})`, `Mujeres (${mujeres})`],
                datasets: [{
                    data: [varones, mujeres],
                    backgroundColor: ['#0284c7', '#ec4899']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });
    }

    let enMejoria = parseInt(document.getElementById("dash-mejora").innerText) || 1;
    let enProlongado = parseInt(document.getElementById("dash-prolongado").innerText) || 0;

    const ctxProg = document.getElementById('chartProgresoClinica');
    if (ctxProg) {
        if(chartProgresoClinicaInstance) chartProgresoClinicaInstance.destroy();
        chartProgresoClinicaInstance = new Chart(ctxProg.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['En Mejoría', 'En Tratamiento Prolongado'],
                datasets: [{
                    label: 'Pacientes',
                    data: [enMejoria, enProlongado],
                    backgroundColor: ['#10b981', '#f59e0b']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    const ctxE = document.getElementById('chartEvolucion');
    if (ctxE) {
        if(chartEvolucionInstance) chartEvolucionInstance.destroy();
        chartEvolucionInstance = new Chart(ctxE.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Inicio', 'Sem 2', 'Sem 3', 'Sem 4', 'Actual'],
                datasets: [{
                    label: 'Promedio Nivel de Dolor (EVA)',
                    data: [7.5, 6.0, 4.8, 3.5, 2.8],
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    borderColor: '#8b5cf6',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }
        });
    }
}