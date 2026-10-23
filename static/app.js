let currentRol = 'paciente';

document.addEventListener("DOMContentLoaded", () => {
    iniciarRelojPeru();
    generarCalendarioWidget();
});

// Reloj Digital Oficial Perú (UTC-5)
function iniciarRelojPeru() {
    setInterval(() => {
        const ahora = new Date();
        const opcionesHora = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        const opcionesFecha = { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' };
        
        document.getElementById("peru-clock").innerText = ahora.toLocaleTimeString('es-PE', opcionesHora);
        document.getElementById("peru-date").innerText = ahora.toLocaleDateString('es-PE', opcionesFecha);
    }, 1000);
}

// Selector de Rol
function seleccionarRol(rol) {
    currentRol = rol;
    document.getElementById("btn-role-paciente").classList.toggle("active", rol === 'paciente');
    document.getElementById("btn-role-admin").classList.toggle("active", rol === 'admin');
    document.getElementById("group-pass").classList.toggle("hidden", rol === 'paciente');
}

// Iniciar Sesión
function iniciarSesion(e) {
    e.preventDefault();
    const dni = document.getElementById("login-dni").value;

    if (!dni) return;

    document.getElementById("login-modal").classList.add("hidden");
    
    const badge = document.getElementById("badge-rol");
    badge.innerText = currentRol.toUpperCase();
    badge.className = `badge-role ${currentRol}`;

    if (currentRol === 'paciente') {
        document.getElementById("portal-paciente").classList.remove("hidden");
        document.getElementById("portal-admin").classList.add("hidden");
        document.getElementById("user-display-name").innerText = `Paciente DNI: ${dni}`;
        document.getElementById("p-dni").innerText = dni;
    } else {
        document.getElementById("portal-paciente").classList.add("hidden");
        document.getElementById("portal-admin").classList.remove("hidden");
        document.getElementById("user-display-name").innerText = "Administrador del Sistema";
    }
}

function cerrarSesion() {
    document.getElementById("login-modal").classList.remove("hidden");
}

// Reprogramar Cita
function reprogramarCita(e) {
    e.preventDefault();
    const fecha = document.getElementById("rep-fecha").value;
    const motivo = document.getElementById("rep-motivo").value;

    alert(`✅ Solicitud enviada correctamente.\nNueva fecha solicitada: ${fecha}\nMotivo enviado: ${motivo}`);
}

// Inferencia Machine Learning
function ejecutarPrediccionIA(e) {
    e.preventDefault();
    const tsk = parseInt(document.getElementById("adm-tsk").value);
    const pcs = parseInt(document.getElementById("adm-pcs").value);
    const asistencia = parseInt(document.getElementById("adm-asistencia").value);

    const score = (tsk + pcs) - (asistencia / 2);
    let nivel = "BAJO";

    if (score > 40) nivel = "ALTO";
    else if (score > 20) nivel = "MODERADO";

    const box = document.getElementById("ia-result-box");
    const badge = document.getElementById("ia-badge");
    
    badge.innerText = `RIESGO EVALUADO: ${nivel}`;
    badge.style.borderColor = nivel === 'ALTO' ? '#ef4444' : (nivel === 'MODERADO' ? '#f59e0b' : '#10b981');
    badge.style.color = badge.style.borderColor;
    
    box.classList.remove("hidden");
}

// Calendario Activo
function generarCalendarioWidget() {
    const widget = document.getElementById("calendar-widget");
    if (!widget) return;
    
    let html = '<div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; text-align:center; font-size:0.85rem;">';
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    
    dias.forEach(d => html += `<strong style="color:var(--accent-cyan);">${d}</strong>`);
    
    for (let i = 1; i <= 31; i++) {
        let style = (i === 26) ? 'background:var(--accent-cyan); color:#000; font-weight:800;' : 'background:rgba(255,255,255,0.05); color:#fff;';
        html += `<div style="padding:8px; border-radius:6px; ${style}">${i}</div>`;
    }
    html += '</div>';
    widget.innerHTML = html;
}