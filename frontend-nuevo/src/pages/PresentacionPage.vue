<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h5>Presentaciones</h5>
      </div>
      <div class="col-auto">
        <Can I="create" an="Presentacion">
          <q-btn color="primary" label="Nueva presentación" icon="add" @click="openDialog()" />
        </Can>
      </div>
    </div>

    <div class="row items-center q-mb-md">
      <div class="col-xs-12 col-sm-6">
        <q-input v-model="filter" label="Buscar por referencia" dense outlined />
      </div>
      <div class="col-xs-12 col-sm-6 text-right">
        <q-btn-toggle
          v-model="mostrarFinalizadas"
          :options="[
            { label: 'Activas', value: false },
            { label: 'Finalizadas', value: true }
          ]"
          color="primary"
          toggle-color="secondary"
          unelevated
        />
      </div>
    </div>

    <q-table :rows="presentacionesFiltradas" :columns="columns" row-key="uuid" flat bordered :filter="filter">
      <template v-slot:body-cell-acciones="props">
        <q-td align="right">
          <Can I="finish" an="Presentacion">
            <q-btn
              dense
              flat
              color="secondary"
              icon="swap_horiz"
              @click.stop="cambiarEstado(props.row)"
              v-ripple
              title="Cambiar estado"
              :disable="bloquearFinalizado(props.row)"
            />
          </Can>
          <Can I="detail" an="Presentacion">
            <q-btn
              dense
              flat
              color="primary"
              icon="receipt"
              @click.stop="emitirRemision(props.row)"
              v-ripple
              title="Emitir remisión"
              :disable="bloquearFinalizado(props.row)"
            />
          </Can>
          <Can I="update" an="Presentacion">
            <q-btn
              dense
              flat
              color="accent"
              icon="edit"
              @click.stop="openDialog(props.row)"
              v-ripple
              title="Editar"
              :disable="bloquearFinalizado(props.row)"
            />
          </Can>
          <Can I="delete" an="Presentacion">
            <q-btn
              dense
              flat
              color="negative"
              icon="delete"
              @click.stop="deleteRegistro(props.row.uuid)"
              v-ripple
              title="Eliminar"
              :disable="bloquearFinalizado(props.row)"
            />
          </Can>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 500px; max-width: 95vw;">
        <q-card-section>
          <div class="text-h6">{{ editing ? 'Editar' : 'Agregar' }} presentación</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="savePresentacion">
            <!-- Referencia -->
            <div class="row q-col-gutter-md">
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
                <q-input filled label="Número de orden" v-model="form.numero_orden" dense :readonly="true" />
              </div>
            </div>

            <!-- Cortes asociados -->
            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-12">
                <q-select
                  filled
                  label="Cortes asociados"
                  v-model="form.cortes_input"
                  :options="cortesFiltrados"
                  option-label="label"
                  option-value="value"
                  multiple
                  emit-value
                  map-options
                  use-chips
                  dense
                />
              </div>
            </div>

            <!-- Fecha y Número de remisión -->
            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Fecha" type="date" v-model="form.fecha" dense />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Número de remisión" v-model="form.numero_remision" dense :readonly="true" />
              </div>
            </div>

            <!-- Estado y Fecha de finalización -->
            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-xs-12 col-sm-6">
                <q-select
                  filled
                  label="Estado"
                  v-model="form.estado_proceso"
                  :options="estadoOptions"
                  emit-value
                  map-options
                  dense
                />
              </div>
              <div class="col-xs-12 col-sm-6">
                <q-input filled label="Fecha de finalización" type="date" v-model="form.fecha_finalizacion" dense />
              </div>
            </div>

            <q-card-actions align="right" class="q-mt-md">
              <q-btn flat label="Cancelar" color="negative" @click="dialog = false" />
              <q-btn flat label="Guardar" color="primary" @click="savePresentacion" />
            </q-card-actions>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { ability } from 'src/services/ability'
import Swal from 'sweetalert2'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

const presentaciones = ref([])
const programaciones = ref([])
const cortes = ref([])
const dialog = ref(false)
const editing = ref(false)
const editingUuid = ref(null)
const filter = ref('')
const mostrarFinalizadas = ref(false)

const auth = useAuthStore()

const bloquearFinalizado = (row) => row.estado_proceso === 'FIN' && !auth.isAdmin

const form = ref({
  referencia: '',
  numero_orden: '',
  fecha: new Date().toISOString().split('T')[0],
  numero_remision: '',
  estado_proceso: 'PEN',
  fecha_finalizacion: '',
  cortes_input: []
})

const estadoOptions = [
  { label: 'Pendiente', value: 'PEN' },
  { label: 'En proceso', value: 'PRO' },
  { label: 'Finalizado', value: 'FIN' }
]

const columns = [
  { name: 'fecha', label: 'Fecha', field: 'fecha' },
  { name: 'numero_orden', label: 'Número de orden', field: 'numero_orden' },
  { name: 'referencia', label: 'Referencia', field: 'referencia' },
  { name: 'numero_remision', label: 'Remisión', field: 'numero_remision' },
  { name: 'estado_proceso', label: 'Estado', field: 'estado_proceso' },
  { name: 'acciones', label: 'Acciones', field: 'uuid' }
]


const cortesFiltrados = computed(() => {
  if (!form.value.referencia) return []
  const selectedProg = programaciones.value.find(p => p.uuid === form.value.referencia)
  if (!selectedProg) return []
  return cortes.value
    .filter(c => c.orden_produccion === selectedProg.numero_orden)
    .map(c => ({ label: c.lote || c.orden_produccion || c.uuid, value: c.uuid }))
})

watch(() => form.value.referencia, (newVal) => {
  if (newVal) {
    form.value.cortes_input = []
    const nextNumber = (presentaciones.value.filter(p => {
      const prog = programaciones.value.find(pr => pr.uuid === newVal)
      return p.referencia === prog?.numero_orden
    }).length + 1)
    form.value.numero_orden = `ORD-${String(nextNumber).padStart(4, '0')}`
    form.value.numero_remision = generarNumeroRemision()
  }
})

const presentacionesActivas = computed(() => presentaciones.value.filter(p => p.estado_proceso !== 'FIN'))
const presentacionesFinalizadas = computed(() => presentaciones.value.filter(p => p.estado_proceso === 'FIN'))
const presentacionesFiltradas = computed(() => (mostrarFinalizadas.value ? presentacionesFinalizadas.value : presentacionesActivas.value))

onMounted(() => {
  loadProgramaciones()
  loadCortes()
  loadPresentaciones()
})

async function loadProgramaciones() {
  try {
    const r = await api.get('core/programacion/')
    programaciones.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadCortes() {
  try {
    const r = await api.get('core/corte/')
    cortes.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadPresentaciones() {
  try {
    const r = await api.get('core/presentacion/')
    presentaciones.value = r.data
  } catch (err) {
    console.error(err)
  }
}

function generarNumeroRemision() {
  const existing = presentaciones.value
  const next = existing.length + 1
  return `REM-${String(next).padStart(4, '0')}`
}

function openDialog(row = null) {
  if (row && !ability.can('update', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para editar presentaciones.', 'warning')
    return
  }
  if (!row && !ability.can('create', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para crear presentaciones.', 'warning')
    return
  }

  if (row) {
    editing.value = true
    editingUuid.value = row.uuid
    const selectedProg = programaciones.value.find(p => p.uuid === row.programacion?.uuid)
    Object.assign(form.value, {
      referencia: selectedProg?.uuid || '',
      numero_orden: row.numero_orden,
      fecha: row.fecha,
      numero_remision: row.numero_remision,
      estado_proceso: row.estado_proceso,
      fecha_finalizacion: row.fecha_finalizacion,
      cortes_input: (row.cortes || []).map(c => c.uuid)
    })
  } else {
    editing.value = false
    editingUuid.value = null
    Object.assign(form.value, {
      referencia: '',
      numero_orden: '',
      fecha: new Date().toISOString().split('T')[0],
      numero_remision: '',
      estado_proceso: 'PEN',
      fecha_finalizacion: '',
      cortes_input: []
    })
  }
  dialog.value = true
}

async function savePresentacion() {
  if (editing.value && !ability.can('update', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para actualizar presentaciones.', 'warning')
    return
  }
  if (!editing.value && !ability.can('create', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para crear presentaciones.', 'warning')
    return
  }

  try {
    const selectedProg = programaciones.value.find(p => p.uuid === form.value.referencia)
    const payload = {
      programacion_uuid: form.value.referencia || null,
      numero_orden: form.value.numero_orden,
      referencia: selectedProg?.numero_orden || '',
      fecha: form.value.fecha,
      estado_proceso: form.value.estado_proceso,
      fecha_finalizacion: form.value.fecha_finalizacion,
      cortes_input: form.value.cortes_input
    }

    if (editing.value && editingUuid.value) {
      await api.put(`core/presentacion/${editingUuid.value}/`, payload)
      Swal.fire('Éxito', 'Presentación actualizada', 'success')
    } else {
      await api.post('core/presentacion/', payload)
      Swal.fire('Éxito', 'Presentación registrada', 'success')
    }

    dialog.value = false
    await loadPresentaciones()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', err?.response?.data?.detail || 'No se pudo guardar', 'error')
  }
}

async function deleteRegistro(uuid) {
  if (!ability.can('delete', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para eliminar presentaciones.', 'warning')
    return
  }

  const item = presentaciones.value.find(p => p.uuid === uuid)
  if (item && item.estado_proceso === 'FIN' && !auth.isAdmin) {
    Swal.fire('Atención', 'La presentación finalizada no puede eliminarse.', 'warning')
    return
  }

  try {
    await api.delete(`core/presentacion/${uuid}/`)
    Swal.fire('Eliminado', 'Presentación eliminada', 'success')
    await loadPresentaciones()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo eliminar', 'error')
  }
}

async function cambiarEstado(row) {
  if (!ability.can('finish', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para cambiar el estado de las presentaciones.', 'warning')
    return
  }
  if (row.estado_proceso === 'FIN' && !auth.isAdmin) {
    Swal.fire('Atención', 'La presentación ya está finalizada y no puede cambiarse.', 'warning')
    return
  }

  const inputOptions = {
    PEN: 'Pendiente',
    PRO: 'En proceso',
    FIN: 'Finalizado'
  }

  const { value: nuevoEstado } = await Swal.fire({
    title: 'Selecciona el nuevo estado',
    input: 'select',
    inputOptions,
    inputValue: row.estado_proceso,
    showCancelButton: true,
    inputValidator: (value) => {
      if (!value) {
        return 'Debes seleccionar un estado'
      }
      if (value === row.estado_proceso) {
        return 'Selecciona un estado diferente'
      }
      return null
    }
  })

  if (!nuevoEstado) return

  try {
    await api.patch(`core/presentacion/${row.uuid}/`, { estado_proceso: nuevoEstado })
    Swal.fire('Éxito', `Estado cambiado a ${inputOptions[nuevoEstado]}`, 'success')
    await loadPresentaciones()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo cambiar el estado', 'error')
  }
}

async function emitirRemision(row) {
  if (!ability.can('detail', 'Presentacion')) {
    Swal.fire('Permiso denegado', 'No tienes permiso para emitir remisiones de presentación.', 'warning')
    return
  }

  const html = `
    <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto;">
      <h1 style="text-align: center; color: #333;">Remisión de Presentación</h1>
      <div style="border: 1px solid #ccc; padding: 15px; margin: 20px 0;">
        <h2>Información General</h2>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Referencia:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.referencia}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Número de Orden:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.numero_orden}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Fecha:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.fecha}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Número de Remisión:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.numero_remision}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Estado:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${getEstadoLabel(row.estado_proceso)}</td></tr>
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Cortes Asociados:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.cortes?.length || 0}</td></tr>
        </table>
      </div>
      ${row.fecha_finalizacion ? `
      <div style="border: 1px solid #ccc; padding: 15px; margin: 20px 0;">
        <h2>Finalización</h2>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Fecha de Finalización:</strong></td><td style="padding: 5px; border: 1px solid #ddd;">${row.fecha_finalizacion}</td></tr>
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

    pdf.save(`presentacion_${row.numero_remision}.pdf`)
  } catch (error) {
    console.error('Error generando PDF:', error)
    Swal.fire('Error', 'No se pudo generar el PDF', 'error')
  } finally {
    document.body.removeChild(element)
  }
}

function getEstadoLabel(estado) {
  const opt = estadoOptions.find(o => o.value === estado)
  return opt?.label || estado
}
</script>
