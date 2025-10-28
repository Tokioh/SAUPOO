const uploadForm = document.getElementById('uploadForm')
const ofertaFile = document.getElementById('ofertaFile')
const postFile = document.getElementById('postFile')
const uploadStatus = document.getElementById('uploadStatus')
const btnEjecutar = document.getElementById('btnEjecutar')
const btnVerResultados = document.getElementById('btnVerResultados')
const btnDescargarResultados = document.getElementById('btnDescargarResultados')
const actionStatus = document.getElementById('actionStatus')
const resultsArea = document.getElementById('resultsArea')

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  uploadStatus.textContent = ''
  uploadStatus.classList.remove('error')
  uploadStatus.classList.add('busy')
  uploadStatus.textContent = 'Subiendo...'
  const fd = new FormData()
  if (ofertaFile.files[0]) fd.append('oferta', ofertaFile.files[0])
  if (postFile.files[0]) fd.append('postulaciones', postFile.files[0])

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd })
    const text = await res.text()
    let parsed = null
    try {
      parsed = JSON.parse(text)
    } catch (e) {
      // no JSON
    }

    if (res.ok && parsed && parsed.saved !== undefined) {
      uploadStatus.classList.remove('busy')
      uploadStatus.textContent = 'Archivos guardados: ' + JSON.stringify(parsed.saved)
    } else {
      uploadStatus.classList.remove('busy')
      uploadStatus.classList.add('error')
      if (parsed && parsed.error) {
        uploadStatus.textContent = 'Error: ' + parsed.error
      } else {
        uploadStatus.textContent = `Error subiendo archivos (status ${res.status}). Respuesta: ${text}`
      }
      console.error('Upload failed', res.status, text)
    }
  } catch (err) {
    uploadStatus.classList.remove('busy')
    uploadStatus.classList.add('error')
    uploadStatus.textContent = 'Error subiendo archivos (network).'
    console.error(err)
  }
})

btnEjecutar.addEventListener('click', async () => {
  actionStatus.textContent = 'Iniciando ejecución...'
  try {
    const res = await fetch('/api/ejecutar', { method: 'POST' })
    const json = await res.json()
    actionStatus.textContent = 'Estado: ' + JSON.stringify(json)
  } catch (err) {
    actionStatus.textContent = 'Error al ejecutar.'
  }
})

btnVerResultados.addEventListener('click', async () => {
  resultsArea.textContent = 'Cargando resultados...'
  try {
    const res = await fetch('/api/resultados')
    if (res.status === 200) {
      const text = await res.text()
      // mostrar tabla simple
      const rows = text.split('\n').filter(r => r.trim())
      let html = '<table class="results-table" cellpadding="6"><thead>'
      if (rows.length) {
        const cols = rows[0].split(',')
        html += '<tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>'
        for (let i = 1; i < rows.length; i++) {
          const cols = rows[i].split(',')
          html += '<tr>' + cols.map(c => `<td>${c}</td>`).join('') + '</tr>'
        }
        html += '</tbody></table>'
      } else {
        html = '(archivo vacío)'
      }
      resultsArea.innerHTML = html
    } else {
      let text = ''
      try { text = await res.text() } catch(e){}
      resultsArea.textContent = 'No hay resultados: ' + (text || res.status)
    }
  } catch (err) {
    resultsArea.textContent = 'Error cargando resultados.'
    console.error(err)
  }
})

btnDescargarResultados.addEventListener('click', async () => {
  actionStatus.textContent = 'Descargando CSV...'
  try {
    const res = await fetch('/api/resultados')
    if (!res.ok) {
      const text = await res.text()
      actionStatus.textContent = 'No se pudo descargar: ' + (text || res.status)
      return
    }
    const blob = await res.blob()
    // intentar obtener filename desde header
    const cd = res.headers.get('content-disposition') || ''
    let filename = 'asignacion_resultados.csv'
    const m = cd.match(/filename\*=UTF-8''([^;\n]+)/i) || cd.match(/filename="?([^";\n]+)"?/i)
    if (m && m[1]) filename = decodeURIComponent(m[1])

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    actionStatus.textContent = 'Descarga iniciada.'
  } catch (err) {
    actionStatus.textContent = 'Error al descargar archivo.'
    console.error(err)
  }
})
