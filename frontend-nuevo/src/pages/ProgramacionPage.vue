<template>
  <q-page class="q-pa-md q-gutter-sm">
    <div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div>
          <q-space />

          <div class="row items-center q-mb-sm">
            <Can I="create" an="Programacion">
              <q-btn unelevated rounded icon="add" color="primary" @click="creating" label="Agregar" />
            </Can>
            <q-space />
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-xs-12 col-sm-6 col-md-4" v-for="item in programaciones" :key="item.uuid">
              <q-card class="my-card">
                <q-card-section class="row items-center">
                  <div>
                    <div class="text-subtitle2 text-weight-medium">{{ item.numero_orden }}</div>
                    <div class="text-caption">{{ item.codigo }}</div>
                  </div>
                  <q-space />
                  <q-btn color="secondary" size="sm" label="Insumos" @click="openInsumos(item)" />
                </q-card-section>
                <q-separator />
                <q-card-section>
                  <div class="text-caption">{{ item.descripcion }}</div>
                  <div class="text-caption q-mt-sm">Proveedor: {{ item.proveedor ? item.proveedor.nombre : '-' }}</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <q-separator class="q-mt-md" />

          <div class="q-mt-md">
            <div class="text-h6">Historial de solicitudes</div>
            <q-table :rows="programaciones" :columns="histColumns" row-key="uuid" flat dense>
              <template v-slot:body-cell-acciones="props">
                <q-td :props="props">
                  <q-btn flat dense icon="visibility" size="sm" color="primary" @click="openDetailDialog(props.row)" label="Ver" />
                </q-td>
              </template>
            </q-table>
          </div>

        </div>
      </transition>

      <!-- Dialog: Nueva Programación -->
      <q-dialog v-model="toolbar" persistent>
        <q-card style="width: 700px; max-width: 95vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Nueva Programación</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="toolbar=false" />
          </q-card-section>

          <q-linear-progress :value="1" color="primary" />

          <q-card-section class="q-pt-md">
            <q-form ref="form_ref" @submit.prevent="onSubmit" class="q-gutter-md">
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-6">
                  <q-input filled v-model="numero_orden" label="Número de orden *" lazy-rules dense :rules="[val => !!val || 'El campo es obligatorio']" />
                </div>
                <div class="col-xs-12 col-sm-6">
                  <q-input filled v-model="codigo" label="Código *" lazy-rules dense :rules="[val => !!val || 'El campo es obligatorio']" />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-input filled v-model="descripcion" label="Descripción" type="textarea" rows="2" dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-select filled v-model="proveedor" :options="proveedores" option-value="uuid" option-label="nombre" label="Proveedor" emit-value map-options dense />
                </div>
              </div>
            </q-form>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" v-close-popup color="negative" flat @click="toolbar=false" />
            <q-btn label="Guardar" @click.prevent="onSubmit" color="primary" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Dialog: Insumos -->
      <q-dialog v-model="insumosToolbar" persistent>
        <q-card style="width: 900px; max-width: 95vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Insumos - {{ activeProgramacion ? activeProgramacion.numero_orden : '' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="insumosToolbar=false" />
          </q-card-section>

          <q-card-section>
            <div>
              <q-input dense debounce="300" v-model="filterInv" placeholder="Buscar inventario" />
              <q-table dense :rows="inventario" :columns="invColumns" :filter="filterInv" row-key="uuid" selection="multiple" v-model:selected="selected" />
            </div>

            <div v-if="selected.length" class="q-mt-md">
              <div class="text-subtitle2">Asignar cantidades</div>
              <div class="row q-col-gutter-md q-mt-sm" v-for="sel in selected" :key="sel.uuid">
                <div class="col-xs-8">{{ sel.nombre }} (Disponibilidad: {{ sel.cantidad }})</div>
                <div class="col-xs-4">
                  <q-input filled v-model.number="selectedQtyMap[sel.uuid]" type="number" min="1" dense />
                </div>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" v-close-popup color="negative" flat @click="insumosToolbar=false" />
            <q-btn label="Solicitar" color="primary" @click="onSubmitInsumos" :disable="!selected.length" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Dialog: Detalle de Solicitud -->
      <q-dialog v-model="detailDialog" :maximized="false">
        <q-card style="width: 600px; max-width: 95vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Detalle de solicitud - {{ selectedSolicitud ? selectedSolicitud.numero_orden : '' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pt-md" v-if="selectedSolicitud">
            <div class="q-mb-md">
              <div class="text-subtitle2">Información general</div>
              <div class="q-mt-sm">
                <div><strong>Orden:</strong> {{ selectedSolicitud.numero_orden }}</div>
                <div><strong>Código:</strong> {{ selectedSolicitud.codigo }}</div>
                <div><strong>Descripción:</strong> {{ selectedSolicitud.descripcion }}</div>
                <div><strong>Proveedor:</strong> {{ selectedSolicitud.proveedor ? selectedSolicitud.proveedor.nombre : '-' }}</div>
              </div>
            </div>

            <q-separator />

            <div class="q-mt-md">
              <div class="text-subtitle2">Productos solicitados</div>
              <q-table
                v-if="selectedSolicitud.insumos && selectedSolicitud.insumos.length"
                :rows="selectedSolicitud.insumos"
                :columns="insumosDetailColumns"
                row-key="uuid"
                flat
                dense
              />
              <div v-else class="text-caption text-grey">No hay insumos solicitados</div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cerrar" v-close-popup color="primary" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'
import { useAuthStore } from 'src/stores/auth'

const toolbar = ref(false)
const insumosToolbar = ref(false)
const numero_orden = ref(null)
const codigo = ref(null)
const descripcion = ref(null)
const proveedor = ref(null)
const proveedores = ref([])
const programaciones = ref([])
const inventario = ref([])
const selected = ref([]) // array of selected rows from inventory
const selectedQtyMap = ref({}) // tracks quantities for selected items
const filterInv = ref(null)
const historial = ref([])
const activeProgramacion = ref(null)
const form_ref = ref(null)
const auth = useAuthStore()
const detailDialog = ref(false)
const selectedSolicitud = ref(null)

const histColumns = [
  { name: 'programacion', label: 'Orden', field: row => (row.numero_orden ? row.numero_orden : ''), align: 'left' },
  { name: 'total_insumos', label: 'Productos', field: row => (row.insumos ? row.insumos.length : 0), align: 'center' },
  { name: 'created', label: 'Fecha', field: 'created', align: 'center' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

const invColumns = [
  { name: 'codigo', label: 'Código', field: 'codigo', sortable: true },
  { name: 'nombre', label: 'Nombre', field: 'nombre', sortable: true },
  { name: 'cantidad', label: 'Disponibilidad', field: 'cantidad', sortable: true },
]

const insumosDetailColumns = [
  { name: 'codigo', label: 'Código', field: row => row.inventario ? row.inventario.codigo : '', align: 'left' },
  { name: 'nombre', label: 'Nombre', field: row => row.inventario ? row.inventario.nombre : '', align: 'left' },
  { name: 'cantidad', label: 'Cantidad', field: 'cantidad', align: 'center' },
  { name: 'created', label: 'Fecha', field: 'created', align: 'center' }
]

onMounted(() => {
  loadProgramaciones()
  loadProveedores()
  loadHistorial()
})

async function loadProgramaciones() {
  try {
    const r = await api.get('core/programacion/')
    programaciones.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadProveedores() {
  try {
    const r = await api.get('core/proveedor/')
    proveedores.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadInventario() {
  try {
    const r = await api.get('core/inventario/')
    inventario.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadHistorial() {
  try {
    // listar todas las programaciones con sus insumos
    const r = await api.get('core/programacion/')
    historial.value = r.data
  } catch (err) {
    console.error(err)
  }
}

function creating() {
  numero_orden.value = null
  codigo.value = null
  descripcion.value = null
  proveedor.value = null
  toolbar.value = true
}

async function onSubmit() {
  const valid = await (form_ref.value ? form_ref.value.validate() : true)
  if (!valid) return
  try {
    await api.post('core/programacion/', {
      numero_orden: numero_orden.value,
      codigo: codigo.value,
      descripcion: descripcion.value,
      proveedor: proveedor.value
    })
    toolbar.value = false
    await loadProgramaciones()
    await loadHistorial()
    Swal.fire({ title: 'Éxito', text: 'Programación creada', icon: 'success' })
  } catch (err) {
    console.error(err)
    Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo crear', icon: 'error' })
  }
}

function openInsumos(p) {
  activeProgramacion.value = p
  selected.value = []
  selectedQtyMap.value = {}
  loadInventario()
  insumosToolbar.value = true
}

const selectedWithQty = computed(() => {
  return selected.value.map(s => ({
    ...s,
    cantidad_asignada: selectedQtyMap.value[s.uuid] || 1
  }))
})

function openDetailDialog(programacion) {
  selectedSolicitud.value = programacion
  detailDialog.value = true
}

async function onSubmitInsumos() {
  // prepare items using quantities from selectedQtyMap
  const items = selected.value.map(s => ({
    inventario: s.uuid,
    cantidad: Number(selectedQtyMap.value[s.uuid]) || 1
  }))
  try {
    await api.post(`core/programacion/${activeProgramacion.value.uuid}/insumos/`, { items })
    insumosToolbar.value = false
    selected.value = []
    selectedQtyMap.value = {}
    Swal.fire({ title: 'Éxito', text: 'Insumos solicitados y descontados del inventario', icon: 'success' })
    // refresh programaciones and historial and inventario
    await loadProgramaciones()
    await loadHistorial()
    // notify other pages to reload inventario (e.g., InventarioPage)
    window.dispatchEvent(new CustomEvent('inventario-updated'))
  } catch (err) {
    console.error(err)
    Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo solicitar insumos', icon: 'error' })
  }
}

</script>

<style scoped>
.my-card { margin-bottom: 12px }
</style>