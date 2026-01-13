/**
 * SAUPOO - Sistema de Asignación Universitaria
 * Frontend JavaScript - Gestión de Rondas y Períodos
 */

// ============================================================================
// ELEMENTOS DEL DOM
// ============================================================================

// Navegación
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.section');

// Sección Asignación
const formAsignacion = document.getElementById('form-asignacion');
const inputAnio = document.getElementById('anio');
const inputSemestre = document.getElementById('semestre');
const inputArchivoOferta = document.getElementById('archivo-oferta');
const inputArchivoPostulaciones = document.getElementById('archivo-postulaciones');
const inputObservaciones = document.getElementById('observaciones');
const dropOferta = document.getElementById('drop-oferta');
const dropPostulaciones = document.getElementById('drop-postulaciones');
const nombreOferta = document.getElementById('nombre-oferta');
const nombrePostulaciones = document.getElementById('nombre-postulaciones');
const btnEjecutar = document.getElementById('btn-ejecutar');
const resultadoAsignacion = document.getElementById('resultado-asignacion');
const statsAsignacion = document.getElementById('stats-asignacion');
const btnDescargarResultado = document.getElementById('btn-descargar-resultado');
const btnNuevaAsignacion = document.getElementById('btn-nueva-asignacion');

// Sección Registros
const filtroAnio = document.getElementById('filtro-anio');
const filtroSemestre = document.getElementById('filtro-semestre');
const btnFiltrar = document.getElementById('btn-filtrar');
const btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
const periodosContainer = document.getElementById('periodos-container');
const tbodyRondas = document.getElementById('tbody-rondas');
const tablaEmpty = document.getElementById('tabla-empty');

// Modales
const modalCarga = document.getElementById('modal-carga');
const modalDetalle = document.getElementById('modal-detalle');
const modalDetalleBody = document.getElementById('modal-detalle-body');
const btnCerrarModal = document.getElementById('btn-cerrar-modal');

// Toast
const toastContainer = document.getElementById('toast-container');

// Estado actual
let rondaActual = null;

// ============================================================================
// NAVEGACIÓN
// ============================================================================

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSection = link.dataset.section;
        
        // Actualizar navegación activa
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        // Mostrar sección correspondiente
        sections.forEach(section => {
            section.classList.remove('active');
            if (section.id === `seccion-${targetSection}`) {
                section.classList.add('active');
            }
        });
        
        // Cargar datos si es la sección de registros
        if (targetSection === 'registros') {
            cargarHistorial();
            cargarPeriodos();
        }
    });
});

// ============================================================================
// MANEJO DE ARCHIVOS (DRAG & DROP)
// ============================================================================

function setupFileUpload(dropZone, fileInput, nombreDisplay) {
    // Click para seleccionar archivo
    dropZone.addEventListener('click', () => fileInput.click());
    
    // Cambio de archivo
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            nombreDisplay.textContent = fileInput.files[0].name;
            dropZone.classList.add('has-file');
        } else {
            nombreDisplay.textContent = 'Ningún archivo seleccionado';
            dropZone.classList.remove('has-file');
        }
    });
    
    // Drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'));
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'));
    });
    
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            nombreDisplay.textContent = files[0].name;
            dropZone.classList.add('has-file');
        }
    });
}

setupFileUpload(dropOferta, inputArchivoOferta, nombreOferta);
setupFileUpload(dropPostulaciones, inputArchivoPostulaciones, nombrePostulaciones);

// ============================================================================
// FORMULARIO DE ASIGNACIÓN
// ============================================================================

formAsignacion.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Validar archivos
    if (!inputArchivoOferta.files[0] || !inputArchivoPostulaciones.files[0]) {
        showToast('Por favor selecciona ambos archivos CSV', 'error');
        return;
    }
    
    // Mostrar modal de carga
    modalCarga.classList.remove('hidden');
    btnEjecutar.disabled = true;
    
    // Preparar FormData
    const formData = new FormData();
    formData.append('archivo_oferta', inputArchivoOferta.files[0]);
    formData.append('archivo_postulaciones', inputArchivoPostulaciones.files[0]);
    formData.append('anio', inputAnio.value);
    formData.append('semestre', inputSemestre.value);
    
    if (inputObservaciones.value.trim()) {
        formData.append('observaciones', inputObservaciones.value.trim());
    }
    
    try {
        const response = await fetch('/api/ronda/ejecutar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            rondaActual = data.ronda;
            mostrarResultadoAsignacion(data.ronda);
            showToast('¡Asignación completada exitosamente!', 'success');
        } else {
            showToast(data.detail || 'Error al ejecutar la asignación', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión al servidor', 'error');
    } finally {
        modalCarga.classList.add('hidden');
        btnEjecutar.disabled = false;
    }
});

function mostrarResultadoAsignacion(ronda) {
    resultadoAsignacion.classList.remove('hidden');
    
    statsAsignacion.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${ronda.periodo_str}</div>
            <div class="stat-label">Período</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">#${ronda.numero}</div>
            <div class="stat-label">Ronda</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${ronda.total_aspirantes}</div>
            <div class="stat-label">Aspirantes</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${ronda.total_asignados}</div>
            <div class="stat-label">Asignados</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${ronda.total_no_asignados}</div>
            <div class="stat-label">No Asignados</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${ronda.tasa_asignacion}%</div>
            <div class="stat-label">Tasa de Asignación</div>
        </div>
    `;
    
    // Scroll al resultado
    resultadoAsignacion.scrollIntoView({ behavior: 'smooth' });
}

// Botón descargar resultado
btnDescargarResultado.addEventListener('click', () => {
    if (rondaActual) {
        descargarArchivo(
            rondaActual.periodo.anio,
            rondaActual.periodo.semestre,
            rondaActual.numero,
            'resultados'
        );
    }
});

// Botón nueva asignación
btnNuevaAsignacion.addEventListener('click', () => {
    // Resetear formulario
    formAsignacion.reset();
    inputArchivoOferta.value = '';
    inputArchivoPostulaciones.value = '';
    nombreOferta.textContent = 'Ningún archivo seleccionado';
    nombrePostulaciones.textContent = 'Ningún archivo seleccionado';
    dropOferta.classList.remove('has-file');
    dropPostulaciones.classList.remove('has-file');
    resultadoAsignacion.classList.add('hidden');
    rondaActual = null;
    
    // Scroll arriba
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ============================================================================
// SECCIÓN DE REGISTROS
// ============================================================================

async function cargarPeriodos() {
    try {
        const response = await fetch('/api/periodos');
        const data = await response.json();
        
        // Llenar filtro de años
        const aniosUnicos = [...new Set(data.periodos.map(p => p.anio))].sort((a, b) => b - a);
        filtroAnio.innerHTML = '<option value="">Todos</option>';
        aniosUnicos.forEach(anio => {
            filtroAnio.innerHTML += `<option value="${anio}">${anio}</option>`;
        });
        
        // Mostrar tarjetas de períodos
        if (data.periodos.length > 0) {
            periodosContainer.innerHTML = '';
            
            // Obtener resumen de cada período
            for (const periodo of data.periodos) {
                try {
                    const resResponse = await fetch(`/api/periodo/${periodo.anio}/${periodo.semestre}`);
                    const resumen = await resResponse.json();
                    
                    periodosContainer.innerHTML += `
                        <div class="periodo-card">
                            <h3><i class="fas fa-calendar"></i> Período ${resumen.periodo}</h3>
                            <div class="periodo-stats">
                                <span><i class="fas fa-layer-group"></i> ${resumen.total_rondas} rondas</span>
                                <span><i class="fas fa-users"></i> ${resumen.total_asignados} asignados</span>
                            </div>
                        </div>
                    `;
                } catch (e) {
                    console.error('Error cargando resumen:', e);
                }
            }
        } else {
            periodosContainer.innerHTML = '<p style="color: var(--text-secondary);">No hay períodos registrados</p>';
        }
    } catch (error) {
        console.error('Error cargando períodos:', error);
    }
}

async function cargarHistorial(anio = null, semestre = null) {
    try {
        let url = '/api/rondas/historial';
        if (anio && semestre) {
            url += `?anio=${anio}&semestre=${semestre}`;
        } else if (anio) {
            url += `?anio=${anio}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.rondas && data.rondas.length > 0) {
            tablaEmpty.classList.add('hidden');
            tbodyRondas.innerHTML = '';
            
            data.rondas.forEach(ronda => {
                const fechaFormateada = new Date(ronda.fecha_ejecucion).toLocaleString('es-EC', {
                    dateStyle: 'medium',
                    timeStyle: 'short'
                });
                
                tbodyRondas.innerHTML += `
                    <tr>
                        <td><span class="badge badge-primary">${ronda.periodo_str}</span></td>
                        <td><strong>Ronda #${ronda.numero}</strong></td>
                        <td>${fechaFormateada}</td>
                        <td>${ronda.total_aspirantes}</td>
                        <td><span class="badge badge-success">${ronda.total_asignados}</span></td>
                        <td><span class="badge badge-warning">${ronda.total_no_asignados}</span></td>
                        <td class="acciones">
                            <button class="btn btn-sm btn-secondary" onclick="verDetalleRonda(${ronda.periodo.anio}, ${ronda.periodo.semestre}, ${ronda.numero})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-success" onclick="descargarArchivo(${ronda.periodo.anio}, ${ronda.periodo.semestre}, ${ronda.numero}, 'resultados')">
                                <i class="fas fa-download"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
        } else {
            tbodyRondas.innerHTML = '';
            tablaEmpty.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error cargando historial:', error);
        showToast('Error al cargar el historial', 'error');
    }
}

// Filtros
btnFiltrar.addEventListener('click', () => {
    const anio = filtroAnio.value || null;
    const semestre = filtroSemestre.value || null;
    cargarHistorial(anio, semestre);
});

btnLimpiarFiltros.addEventListener('click', () => {
    filtroAnio.value = '';
    filtroSemestre.value = '';
    cargarHistorial();
});

// ============================================================================
// DETALLE DE RONDA
// ============================================================================

async function verDetalleRonda(anio, semestre, numero) {
    try {
        const response = await fetch(`/api/ronda/${anio}/${semestre}/${numero}`);
        const ronda = await response.json();
        
        const fechaFormateada = new Date(ronda.fecha_ejecucion).toLocaleString('es-EC', {
            dateStyle: 'full',
            timeStyle: 'medium'
        });
        
        modalDetalleBody.innerHTML = `
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Período</label>
                    <span>${ronda.periodo_str}</span>
                </div>
                <div class="detail-item">
                    <label>Número de Ronda</label>
                    <span>#${ronda.numero}</span>
                </div>
                <div class="detail-item detail-full">
                    <label>Fecha de Ejecución</label>
                    <span>${fechaFormateada}</span>
                </div>
                <div class="detail-item">
                    <label>Total Aspirantes</label>
                    <span>${ronda.total_aspirantes}</span>
                </div>
                <div class="detail-item">
                    <label>Asignados</label>
                    <span style="color: var(--success-color)">${ronda.total_asignados}</span>
                </div>
                <div class="detail-item">
                    <label>No Asignados</label>
                    <span style="color: var(--warning-color)">${ronda.total_no_asignados}</span>
                </div>
                <div class="detail-item">
                    <label>Tasa de Asignación</label>
                    <span>${ronda.tasa_asignacion}%</span>
                </div>
                ${ronda.observaciones ? `
                <div class="detail-item detail-full">
                    <label>Observaciones</label>
                    <span>${ronda.observaciones}</span>
                </div>
                ` : ''}
            </div>
            <div class="detail-actions">
                <button class="btn btn-secondary" onclick="descargarArchivo(${anio}, ${semestre}, ${numero}, 'resultados')">
                    <i class="fas fa-download"></i> Resultados
                </button>
                <button class="btn btn-outline" onclick="descargarArchivo(${anio}, ${semestre}, ${numero}, 'oferta')">
                    <i class="fas fa-file-csv"></i> Oferta
                </button>
                <button class="btn btn-outline" onclick="descargarArchivo(${anio}, ${semestre}, ${numero}, 'postulaciones')">
                    <i class="fas fa-file-csv"></i> Postulaciones
                </button>
                <button class="btn btn-danger" onclick="eliminarRonda(${anio}, ${semestre}, ${numero})">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        `;
        
        modalDetalle.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar detalle de la ronda', 'error');
    }
}

// Cerrar modal
btnCerrarModal.addEventListener('click', () => {
    modalDetalle.classList.add('hidden');
});

modalDetalle.addEventListener('click', (e) => {
    if (e.target === modalDetalle) {
        modalDetalle.classList.add('hidden');
    }
});

// ============================================================================
// ACCIONES
// ============================================================================

async function descargarArchivo(anio, semestre, numero, tipo) {
    try {
        const response = await fetch(`/api/ronda/${anio}/${semestre}/${numero}/descargar/${tipo}`);
        
        if (!response.ok) {
            throw new Error('No se pudo descargar el archivo');
        }
        
        const blob = await response.blob();
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `${tipo}_${anio}-${semestre}_ronda${numero}.csv`;
        
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^";\n]+)"?/i);
            if (match && match[1]) {
                filename = match[1];
            }
        }
        
        // Crear link de descarga
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('Descarga iniciada', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al descargar archivo', 'error');
    }
}

async function eliminarRonda(anio, semestre, numero) {
    if (!confirm(`¿Estás seguro de eliminar la Ronda #${numero} del período ${anio}-${semestre}?\n\nEsta acción no se puede deshacer.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/ronda/${anio}/${semestre}/${numero}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showToast('Ronda eliminada correctamente', 'success');
            modalDetalle.classList.add('hidden');
            cargarHistorial();
            cargarPeriodos();
        } else {
            showToast(data.detail || 'Error al eliminar la ronda', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al eliminar la ronda', 'error');
    }
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="${icons[type] || icons.success}"></i>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Remover después de 4 segundos
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Establecer año actual por defecto
    const anioActual = new Date().getFullYear();
    inputAnio.value = anioActual;
    
    // Determinar semestre actual
    const mesActual = new Date().getMonth();
    inputSemestre.value = mesActual < 6 ? '1' : '2';
});

// Exponer funciones globalmente para los onclick inline
window.verDetalleRonda = verDetalleRonda;
window.descargarArchivo = descargarArchivo;
window.eliminarRonda = eliminarRonda;
