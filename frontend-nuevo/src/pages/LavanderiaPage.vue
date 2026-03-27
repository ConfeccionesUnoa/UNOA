<template>
  <q-page class="q-pa-md q-gutter-sm">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h5>Lavandería</h5>
      </div>
      <div class="col-auto">
        <q-btn color="primary" label="Nueva solicitud" icon="add" @click="openDialog()" />
      </div>
    </div>

    <div class="row q-mb-md">
      <q-input v-model="filter" label="Buscar por referencia" dense />
    </div>

    <q-table :rows="lavanderias" :columns="columns" row-key="uuid" flat bordered :filter="filter">
      <template v-slot:body-cell-acciones="props">
        <q-td align="right">
          <q-btn dense flat color="primary" icon="receipt" @click.stop="emitirRemision(props.row)" v-ripple title="Emitir remisión" />
          <q-btn dense flat color="accent" icon="edit" @click.stop="openDialog(props.row)" v-ripple title="Editar" />
          <q-btn dense flat color="negative" icon="delete" @click.stop="deleteRegistro(props.row.uuid)" v-ripple title="Eliminar" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 500px; max-width: 95vw;">
        <q-card-section>
          <div class="text-h6">{{ editing ? 'Editar' : 'Agregar' }} solicitud lavandería</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="saveLavanderia">
            <div class="row q-col-gutter-md">
              <div class="col-xs-12 col-sm-6">
                <q-select
                  filled
                  label="Tipo"
                  v-model="form.tipo"
                  :options="[{ label: 'Salida', value: 'SALIDA' }, { label: 'Recepción', value: 'RECEPCION' }]"
                  emit-value
                  map-options
                  dense
                />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-select
                  filled
                  label="Referencia" 
                  v-model="form.referencia"
                  :options="programaciones.map(p => ({ label: p.numero_orden, value: p.uuid }))"
                  emit-value
                  map-options
                  dense
                />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-select
                  filled
                  label="Corte" 
                  v-model="form.corte_uuid"
                  :options="(form.referencia ? cortes.filter(c => c.orden_produccion === programaciones.find(p => p.uuid === form.referencia)?.numero_orden) : []).map(c => ({ label: c.lote || c.orden_produccion || c.uuid, value: c.uuid }))"
                  option-value="value"
                  option-label="label"
                  :disable="!form.referencia"
                  dense
                />
              </div>
              <div v-if="form.tipo === 'RECEPCION'" class="col-xs-12 col-sm-6">
                <q-select
                  filled
                  label="Remisión de salida"
                  v-model="form.remision_salida_uuid"
                  :options="salidas.map(s => ({ label: s.numero_remision, value: s.uuid }))"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  dense
                />
              </div>
            </div>

            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Fecha" type="date" v-model="form.fecha" dense />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Número de remisión" v-model="form.numero_remision" dense :readonly="true" />
              </div>
            </div>

            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Lavandería" v-model="form.lavanderia" dense />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Cantidad" type="number" v-model.number="form.cantidad" dense />
              </div>
            </div>

            <q-separator class="q-mt-md q-mb-md" />
            <div v-if="form.tipo === 'RECEPCION'">
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12 col-sm-6">
                  <q-input filled label="Cantidad conformes" type="number" v-model.number="form.cantidad_conformes" dense />
                </div>
                <div class="col-xs-12 col-sm-6">
                  <q-input filled label="Cantidad no conformes" type="number" v-model.number="form.cantidad_no_conformes" dense />
                </div>
              </div>
            </div>

            <q-card-actions align="right">
              <q-btn flat label="Cancelar" color="negative" @click="dialog = false" />
              <q-btn flat label="Guardar" color="primary" @click="saveLavanderia" />
            </q-card-actions>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

const lavanderias = ref([])
const programaciones = ref([])
const cortes = ref([])
const salidas = ref([])
const dialog = ref(false)
const editing = ref(false)
const editingUuid = ref(null)
const filter = ref('')

const form = ref({
  tipo: 'SALIDA',
  referencia: null,
  fecha: new Date().toISOString().split('T')[0],
  numero_remision: '',
  lavanderia: '',
  cantidad: 0,
  corte_uuid: null,
  remision_salida_uuid: null,
  cantidad_conformes: 0,
  cantidad_no_conformes: 0,
})

watch(() => form.value.referencia, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    form.value.corte_uuid = null
  }
})

const columns = [
  { name: 'tipo', label: 'Tipo', field: 'tipo' },
  { name: 'referencia', label: 'Referencia', field: 'referencia' },
  { name: 'fecha', label: 'Fecha', field: 'fecha' },
  { name: 'numero_remision', label: 'Remisión', field: 'numero_remision' },
  { name: 'lavanderia', label: 'Lavandería', field: 'lavanderia' },
  { name: 'cantidad', label: 'Cantidad', field: 'cantidad' },
  { name: 'cantidad_conformes', label: 'Conformes', field: 'cantidad_conformes' },
  { name: 'cantidad_no_conformes', label: 'No conformes', field: 'cantidad_no_conformes' },
  { name: 'acciones', label: 'Acciones', field: 'uuid' }
]

onMounted(() => {
  loadProgramaciones()
  loadCortes()
  loadLavanderias()
  loadSalidas()
})

async function loadCortes() {
  try {
    const r = await api.get('core/corte/')
    cortes.value = r.data
  } catch (err) {
    console.error(err)
  }
}


async function loadProgramaciones() {
  try {
    const r = await api.get('core/programacion/')
    programaciones.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadLavanderias() {
  try {
    const r = await api.get('core/lavanderia/')
    lavanderias.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadSalidas() {
  try {
    const r = await api.get('core/lavanderia/?tipo=SALIDA')
    salidas.value = r.data
  } catch (err) {
    console.error(err)
  }
}

function openDialog(row = null) {
  if (row) {
    editing.value = true
    editingUuid.value = row.uuid
    Object.assign(form.value, {
      tipo: row.tipo,
      referencia: row.programacion?.uuid || null,
      fecha: row.fecha,
      numero_remision: row.numero_remision,
      lavanderia: row.lavanderia,
      cantidad: row.cantidad,
      corte_uuid: row.corte?.uuid || null,
      remision_salida_uuid: row.remision_salida_data?.uuid || null,
      cantidad_conformes: row.cantidad_conformes,
      cantidad_no_conformes: row.cantidad_no_conformes,
    })
  } else {
    editing.value = false
    editingUuid.value = null
    form.value = {
      tipo: 'SALIDA',
      referencia: null,
      fecha: new Date().toISOString().split('T')[0],
      numero_remision: generarNumeroRemision(),
      lavanderia: '',
      cantidad: 0,
      corte_uuid: null,
      remision_salida_uuid: null,
      cantidad_conformes: 0,
      cantidad_no_conformes: 0,
    }
  }
  dialog.value = true
}

function generarNumeroRemision() {
  const existing = lavanderias.value.map(l => {
    const match = l.numero_remision.match(/REM-(\d+)/)
    return match ? parseInt(match[1], 10) : 0
  })
  const maxNum = existing.length > 0 ? Math.max(...existing) : 0
  const next = maxNum + 1
  return `REM-${String(next).padStart(4, '0')}`
}

async function saveLavanderia() {
  try {
    const selectedProgramacion = programaciones.value.find(p => p.uuid === form.value.referencia)
    const payload = {
      tipo: form.value.tipo,
      programacion_uuid: form.value.referencia || null,
      corte_uuid: form.value.corte_uuid && typeof form.value.corte_uuid === 'string' ? form.value.corte_uuid : null,
      remision_salida_uuid: form.value.remision_salida_uuid || null,
      referencia: selectedProgramacion?.numero_orden || '',
      fecha: form.value.fecha,
      numero_remision: form.value.numero_remision,
      lavanderia: form.value.lavanderia,
      cantidad: Number(form.value.cantidad) || 0,
      cantidad_conformes: Number(form.value.cantidad_conformes) || 0,
      cantidad_no_conformes: Number(form.value.cantidad_no_conformes) || 0,
    }

    if (editing.value && editingUuid.value) {
      await api.put(`core/lavanderia/${editingUuid.value}/`, payload)
      Swal.fire('Éxito', 'Solicitud actualizada', 'success')
    } else {
      await api.post('core/lavanderia/', payload)
      Swal.fire('Éxito', 'Solicitud registrada', 'success')
    }

    dialog.value = false
    loadLavanderias()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', err?.response?.data?.detail || 'No se pudo guardar', 'error')
  }
}

async function deleteRegistro(uuid) {
  const result = await Swal.fire({
    title: '¿Estás seguro?',
    text: 'Esta acción no se puede deshacer',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  })

  if (result.isConfirmed) {
    try {
      await api.delete(`core/lavanderia/${uuid}/`)
      Swal.fire('Eliminado', 'Registro eliminado', 'success')
      loadLavanderias()
    } catch (err) {
      console.error(err)
      Swal.fire('Error', 'No se pudo eliminar', 'error')
    }
  }
}

async function emitirRemision(row) {
  const html = `
    <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto;">
      <h1 style="text-align: center; color: #333;">Remisión de Lavandería</h1>
      <div style="border: 1px solid #ccc; padding: 15px; margin: 20px 0;">
        <h2>Información General</h2>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Tipo:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.tipo}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Referencia:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.referencia}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Fecha:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.fecha}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Número de Remisión:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.numero_remision}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Lavandería:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.lavanderia}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Cantidad:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.cantidad}</td></tr>
        </table>
      </div>
      ${row.tipo === 'RECEPCION' ? `
      <div style="border: 1px solid #ccc; padding: 15px; margin: 20px 0;">
        <h2>Recepción</h2>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Cantidad Conforme:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.cantidad_conformes}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Cantidad No Conforme:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.cantidad_no_conformes}</td></tr>
        </table>
      </div>
      ` : ''}
      <div style="text-align: center; margin-top: 30px; font-size: 12px; color: #666;">
        <p>Generado el ${new Date().toLocaleDateString()}</p>
      </div>
    </div>
  `

  const element = document.createElement('div')
  element.innerHTML = html
  element.style.position = 'absolute'
  element.style.left = '-9999px'
  document.body.appendChild(element)

  try {
    const canvas = await html2canvas(element, { scale: 2 })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const pageHeight = 295
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save(`remision_${row.numero_remision}.pdf`)
  } catch (error) {
    console.error('Error generando PDF:', error)
    Swal.fire('Error', 'No se pudo generar el PDF', 'error')
  } finally {
    document.body.removeChild(element)
  }
}
</script>
