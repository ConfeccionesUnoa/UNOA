<template>
  <div class="page-presentacion">
    <q-page padding>
      <div class="row items-center q-mb-md">
        <div class="col">
          <h5>Presentaciones</h5>
        </div>
        <div class="col-auto">
          <q-btn color="primary" label="Nueva presentación" @click="openDialog()" />
        </div>
      </div>

      <q-table :rows="presentaciones" :columns="columns" row-key="uuid">
        <template v-slot:body-cell-actions="props">
          <q-td align="right">
            <q-btn dense flat icon="edit" @click="onEdit(props.row)" />
            <q-btn dense flat icon="delete" color="negative" @click="onDelete(props.row)" />
          </q-td>
        </template>
      </q-table>

      <q-dialog v-model="dialog">
        <q-card style="min-width: 600px; max-width: 90vw;">
          <q-card-section>
            <div class="text-h6">{{ editingItem ? 'Editar' : 'Nueva' }} Presentación</div>
          </q-card-section>

          <q-card-section>
            <q-form ref="form" @submit.prevent="save">
              <div class="row q-col-gutter-md">
                <div class="col-md-6">
                  <q-input filled v-model="formData.numero_orden" label="Número de orden" dense />
                </div>
                <div class="col-md-6">
                  <q-select filled v-model="formData.programacion_uuid" :options="programaciones" option-label="numero_orden" option-value="uuid" label="Programación (opcional)" dense use-chips emit-value map-options />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-md">
                <div class="col-md-6">
                  <q-input filled v-model="formData.referencia" label="Referencia" dense />
                </div>
                <div class="col-md-3">
                  <q-select filled v-model="formData.estado_proceso" :options="estadoOptions" label="Estado" dense />
                </div>
                <div class="col-md-3">
                  <q-input filled v-model="formData.fecha" label="Fecha" type="date" dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-md">
                <div class="col-md-6">
                  <q-input filled v-model="formData.fecha_finalizacion" label="Fecha de finalización" type="date" dense />
                </div>
                <div class="col-md-6">
                  <q-select filled v-model="formData.cortes_input" :options="cortesOptions" option-label="ref" option-value="uuid" label="Cortes asociados" multiple dense emit-value map-options />
                </div>
              </div>

            </q-form>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup @click="closeDialog" />
            <q-btn color="primary" label="Guardar" @click="save" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-page>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const presentaciones = ref([])
const programaciones = ref([])
const cortesOptions = ref([])
const dialog = ref(false)
const editingItem = ref(null)
const form = ref(null)

const formData = ref({
  programacion_uuid: null,
  numero_orden: '',
  fecha: null,
  referencia: '',
  estado_proceso: 'PEN',
  fecha_finalizacion: null,
  cortes_input: []
})

const columns = [
  { name: 'fecha', label: 'Fecha', field: 'fecha', sortable: true },
  { name: 'numero_orden', label: 'Número de orden', field: 'numero_orden' },
  { name: 'referencia', label: 'Referencia', field: 'referencia' },
  { name: 'estado_proceso', label: 'Estado', field: 'estado_proceso' },
  { name: 'fecha_finalizacion', label: 'Fecha finalización', field: 'fecha_finalizacion' },
  { name: 'actions', label: 'Acciones', field: 'actions' }
]

const estadoOptions = [
  { label: 'Pendiente', value: 'PEN' },
  { label: 'En proceso', value: 'PRO' },
  { label: 'Finalizado', value: 'FIN' }
]

async function loadPresentaciones() {
  const res = await api.get('core/presentacion/')
  presentaciones.value = res.data
}

async function loadProgramaciones() {
  const res = await api.get('core/programacion/')
  programaciones.value = res.data.map(p => ({ uuid: p.uuid, numero_orden: p.numero_orden }))
}

async function loadCortes() {
  const res = await api.get('core/corte/')
  cortesOptions.value = res.data.map(c => ({ uuid: c.uuid, ref: c.ref || c.uuid, orden_produccion: c.orden_produccion }))
}

function openDialog() {
  editingItem.value = null
  formData.value = { programacion_uuid: null, numero_orden: '', fecha: null, referencia: '', estado_proceso: 'PEN', fecha_finalizacion: null, cortes_input: [] }
  dialog.value = true
}

function closeDialog() {
  dialog.value = false
}

async function onEdit(row) {
  editingItem.value = row
  formData.value = {
    programacion_uuid: row.programacion || null,
    numero_orden: row.numero_orden,
    fecha: row.fecha,
    referencia: row.referencia,
    estado_proceso: row.estado_proceso,
    fecha_finalizacion: row.fecha_finalizacion,
    cortes_input: (row.cortes || []).map(c => c.uuid)
  }
  dialog.value = true
}

async function save() {
  try {
    const payload = { ...formData.value }
    // si viene programacion_uuid en objeto, asegurar formato uuid
    if (payload.programacion_uuid && typeof payload.programacion_uuid === 'object') payload.programacion_uuid = payload.programacion_uuid.uuid

    if (editingItem.value) {
      await api.put(`core/presentacion/${editingItem.value.uuid}/`, payload)
      $q.notify({ type: 'positive', message: 'Presentación actualizada' })
    } else {
      await api.post('core/presentacion/', payload)
      $q.notify({ type: 'positive', message: 'Presentación creada' })
    }
    dialog.value = false
    loadPresentaciones()
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Error al guardar' })
  }
}

async function onDelete(row) {
  try {
    await api.delete(`/api/v1/core/presentacion/${row.uuid}/`)
    $q.notify({ type: 'positive', message: 'Presentación eliminada' })
    loadPresentaciones()
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Error al eliminar' })
  }
}

onMounted(async () => {
  await loadPresentaciones()
  await loadProgramaciones()
  await loadCortes()
})
</script>

<style scoped>
.page-presentacion {
}
</style>
