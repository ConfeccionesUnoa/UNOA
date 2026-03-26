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

          <div class="row q-col-gutter-md">
            <div class="col-xs-12 col-sm-6 col-md-4" v-for="item in mostrarFinalizadas ? programacionesFinalizadas : programacionesActivas" :key="item.uuid">
              <q-card class="my-card">
                <q-card-section class="row items-center">
                  <div>
                    <div class="text-h5 text-weight-bold text-primary">{{ item.numero_orden }}</div>
                    <div class="text-caption">{{ item.codigo }}</div>
                    <div class="text-caption">Prioridad: 
                      <q-input dense v-model.number="item.prioridad" type="number" min="1" @blur="updatePrioridad(item)" style="width: 60px; display: inline-block;" />
                    </div>
                  </div>
                  <q-space />
                  <div class="q-gutter-xs">
                    <Can I="update" an="Programacion">
                      <q-btn color="orange" size="sm" icon="edit" @click="editar(item)" />
                    </Can>
                    <Can I="delete" an="Programacion">
                      <q-btn color="negative" size="sm" icon="delete" @click="eliminar(item)" />
                    </Can>
                    <q-btn color="secondary" size="sm" label="Insumos" @click="openInsumos(item)" />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section>
                  <div class="text-caption">{{ item.descripcion }}</div>
                  <div class="text-caption q-mt-sm">Proveedor: {{ getProveedorNombre(item.proveedor) }}</div>
                  <div class="text-caption q-mt-sm">Cliente: {{ getClienteNombre(item.cliente) }}</div>
                  <div class="text-caption q-mt-sm" v-if="item.tallas">Total unidades: {{ getTallasTotal(item.tallas) }}</div>
                  <div class="text-caption q-mt-sm" v-if="item.fecha_entrega">Fecha entrega: {{ formatDate(item.fecha_entrega) }} ({{ getDiasRestantes(item.fecha_entrega) }} días)</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <div class="row justify-center q-mt-md">
            <q-btn outline color="primary" icon="history" @click="mostrarHistorial = !mostrarHistorial" :label="mostrarHistorial ? 'Ocultar Historial' : 'Ver Historial'" />
          </div>

          <div v-if="mostrarHistorial" class="q-mt-md">
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
        <q-card style="width: 900px; max-width: 90vw; min-width: 720px;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ editingItem ? 'Editar Programación' : 'Nueva Programación' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="closeDialog" />
          </q-card-section>

          <q-linear-progress :value="1" color="primary" />

          <q-card-section class="q-pt-md">
            <q-form ref="form_ref" @submit.prevent="onSubmit" class="q-gutter-md">
              <div class="row q-col-gutter-md">
                <div class="col-xs-12 col-sm-6">
                  <q-input filled v-model="numero_orden" label="Referencia *" lazy-rules dense :rules="[val => !!val || 'El campo es obligatorio']" />
                </div>
                <div class="col-xs-12 col-sm-6">
                  <q-input filled v-model="codigo" label="Orden de compra *" lazy-rules dense :rules="[val => !!val || 'El campo es obligatorio']" />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-select filled v-model="proveedor" :options="proveedores" option-value="uuid" option-label="nombre" label="Proveedor" emit-value map-options dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-select filled v-model="cliente" :options="clientes" option-value="uuid" option-label="nombre" label="Cliente" emit-value map-options dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-input filled v-model="fecha_entrega" label="Fecha de entrega" type="date" dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <div class="text-subtitle2">Total unidades programadas - Tallas</div>
                  <div class="text-caption q-mb-sm">Tallas en letras (S, M, L, XL, XXL)</div>
                  <div class="row q-col-gutter-sm">
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.s" label="S" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.m" label="M" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.l" label="L" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.xl" label="XL" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.xxl" label="XXL" type="number" @update:model-value="calculateTallaTotal" /></div>
                  </div>
                  <div class="text-caption q-mt-md q-mb-sm">Tallas numéricas (4 - 46)</div>
                  <div class="row q-col-gutter-sm">
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t4" label="4" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t6" label="6" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t8" label="8" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t10" label="10" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t12" label="12" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t14" label="14" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t16" label="16" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t18" label="18" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t20" label="20" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t22" label="22" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t26" label="26" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t28" label="28" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t30" label="30" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t32" label="32" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t34" label="34" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t36" label="36" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t38" label="38" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t40" label="40" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t42" label="42" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t44" label="44" type="number" @update:model-value="calculateTallaTotal" /></div>
                    <div class="col-xs-1"><q-input dense v-model.number="tallas.t46" label="46" type="number" @update:model-value="calculateTallaTotal" /></div>
                  </div>
                  <div class="text-caption q-mt-sm">Total unidades: {{ tallas.total }}</div>
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-12">
                  <q-input filled v-model="descripcion" label="Observaciones" type="textarea" rows="3" dense />
                </div>
              </div>
            </q-form>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" color="negative" flat @click="closeDialog" />
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
                <div><strong>Referencia:</strong> {{ selectedSolicitud.numero_orden }}</div>
                <div><strong>Orden de compra:</strong> {{ selectedSolicitud.codigo }}</div>
                <div><strong>Observaciones:</strong> {{ selectedSolicitud.descripcion }}</div>
                <div><strong>Proveedor:</strong> {{ selectedSolicitud.proveedor ? selectedSolicitud.proveedor.nombre : '-' }}</div>
                <div><strong>Cliente:</strong> {{ selectedSolicitud.cliente ? selectedSolicitud.cliente.nombre : '-' }}</div>
                <div v-if="selectedSolicitud.fecha_entrega"><strong>Fecha entrega:</strong> {{ formatDate(selectedSolicitud.fecha_entrega) }} ({{ getDiasRestantes(selectedSolicitud.fecha_entrega) }} días)</div>
                <div v-if="selectedSolicitud.tallas"><strong>Total unidades:</strong> {{ getTallasTotal(selectedSolicitud.tallas) }}</div>
                <div><strong>Prioridad:</strong> {{ selectedSolicitud.prioridad }}</div>
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
const cliente = ref(null)
const fecha_entrega = ref(null)
const proveedores = ref([])
const clientes = ref([])
const presentaciones = ref([])
const tallas = ref({
  s: 0, m: 0, l: 0, xl: 0, xxl: 0,
  t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0,
  total: 0
})
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
const mostrarFinalizadas = ref(false)
const mostrarHistorial = ref(false)
const editingItem = ref(null)

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
  loadClientes()
  loadHistorial()
  loadPresentaciones()
})

const programacionesActivas = computed(() => {
  return programaciones.value.filter(prog => {
    const tienePresentacionFinalizada = presentaciones.value.some(
      pres => pres.referencia === prog.numero_orden && pres.estado_proceso === 'FIN'
    )
    return !tienePresentacionFinalizada
  })
})

const programacionesFinalizadas = computed(() => {
  return programaciones.value.filter(prog => {
    const tienePresentacionFinalizada = presentaciones.value.some(
      pres => pres.referencia === prog.numero_orden && pres.estado_proceso === 'FIN'
    )
    return tienePresentacionFinalizada
  })
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
    console.error('Error cargando proveedores:', err)
  }
}

async function loadClientes() {
  try {
    const r = await api.get('core/cliente/')
    clientes.value = r.data
  } catch (err) {
    console.error('Error cargando clientes:', err)
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

async function loadPresentaciones() {
  try {
    const r = await api.get('core/presentacion/')
    presentaciones.value = r.data
  } catch (err) {
    console.error(err)
  }
}

function calculateTallaTotal() {
  tallas.value.total = (tallas.value.s || 0) + (tallas.value.m || 0) + (tallas.value.l || 0) + (tallas.value.xl || 0) + (tallas.value.xxl || 0) +
    (tallas.value.t4 || 0) + (tallas.value.t6 || 0) + (tallas.value.t8 || 0) + (tallas.value.t10 || 0) + (tallas.value.t12 || 0) +
    (tallas.value.t14 || 0) + (tallas.value.t16 || 0) + (tallas.value.t18 || 0) + (tallas.value.t20 || 0) + (tallas.value.t22 || 0) +
    (tallas.value.t26 || 0) + (tallas.value.t28 || 0) + (tallas.value.t30 || 0) + (tallas.value.t32 || 0) + (tallas.value.t34 || 0) +
    (tallas.value.t36 || 0) + (tallas.value.t38 || 0) + (tallas.value.t40 || 0) + (tallas.value.t42 || 0) + (tallas.value.t44 || 0) +
    (tallas.value.t46 || 0)
}

async function updatePrioridad(item) {
  try {
    await api.patch(`core/programacion/${item.uuid}/`, { prioridad: item.prioridad })
    await loadProgramaciones()
  } catch (err) {
    console.error(err)
    Swal.fire({ title: 'Error', text: 'No se pudo actualizar prioridad', icon: 'error' })
  }
}

async function getNextPrioridad() {
  try {
    const r = await api.get('core/programacion/')
    const prioridades = r.data.map(p => p.prioridad).filter(p => p > 0).sort((a, b) => a - b)
    let next = 1
    for (const p of prioridades) {
      if (p === next) next++
      else break
    }
    return next
  } catch (err) {
    console.error(err)
    return 1
  }
}

function creating(item = null) {
  editingItem.value = item
  if (item) {
    // Cargar datos para editar
    numero_orden.value = item.numero_orden
    codigo.value = item.codigo
    descripcion.value = item.descripcion
    proveedor.value = item.proveedor ? (item.proveedor.uuid || item.proveedor) : null
    cliente.value = item.cliente ? (item.cliente.uuid || item.cliente) : null
    fecha_entrega.value = item.fecha_entrega
    tallas.value = item.tallas ? JSON.parse(item.tallas) : {
      s: 0, m: 0, l: 0, xl: 0, xxl: 0,
      t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0,
      total: 0
    }
  } else {
    // Limpiar para crear nuevo
    numero_orden.value = null
    codigo.value = null
    descripcion.value = null
    proveedor.value = null
    cliente.value = null
    fecha_entrega.value = null
    tallas.value = {
      s: 0, m: 0, l: 0, xl: 0, xxl: 0,
      t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0,
      total: 0
    }
  }
  toolbar.value = true
}

function editar(item) {
  creating(item)
}

function closeDialog() {
  toolbar.value = false
  editingItem.value = null
}

async function eliminar(item) {
  const result = await Swal.fire({
    title: '¿Estás seguro?',
    text: `¿Deseas eliminar la programación "${item.numero_orden}"?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  })

  if (result.isConfirmed) {
    try {
      await api.delete(`core/programacion/${item.uuid}/`)
      await loadProgramaciones()
      await loadHistorial()
      Swal.fire({ title: 'Eliminado', text: 'Programación eliminada correctamente', icon: 'success' })
    } catch (err) {
      console.error('Error eliminando:', err)
      Swal.fire({ title: 'Error', text: `No se pudo eliminar la programación: ${err.response?.data?.detail || err.message}`, icon: 'error' })
    }
  }
}

async function onSubmit() {
  const valid = await (form_ref.value ? form_ref.value.validate() : true)
  if (!valid) return

  try {
    const data = {
      numero_orden: numero_orden.value,
      codigo: codigo.value,
      descripcion: descripcion.value,
      proveedor_uuid: proveedor.value || null,
      cliente_uuid: cliente.value || null,
      fecha_entrega: fecha_entrega.value,
      tallas: JSON.stringify(tallas.value)
    }

    if (editingItem.value) {
      // Actualizar
      data.prioridad = editingItem.value.prioridad // Mantener la prioridad existente
      await api.patch(`core/programacion/${editingItem.value.uuid}/`, data)
      Swal.fire({ title: 'Éxito', text: 'Programación actualizada', icon: 'success' })
    } else {
      // Crear nuevo
      const nextPrioridad = await getNextPrioridad()
      data.prioridad = nextPrioridad
      await api.post('core/programacion/', data)
      Swal.fire({ title: 'Éxito', text: 'Programación creada', icon: 'success' })
    }

    toolbar.value = false
    editingItem.value = null
    await loadProgramaciones()
    await loadHistorial()
  } catch (err) {
    console.error('Error en onSubmit:', err)
    const action = editingItem.value ? 'actualizar' : 'crear'
    Swal.fire({ title: 'Error', text: `No se pudo ${action} la programación: ${err.response?.data?.detail || err.message}`, icon: 'error' })
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

function getTallasTotal(tallasJson) {
  try {
    const tallas = JSON.parse(tallasJson)
    return tallas.total || 0
  } catch (e) {
    return 0
  }
}

function getNombreEntidad(entity, list) {
  if (!entity) return '-'
  if (typeof entity === 'object') return entity.nombre || entity.uuid || '-'
  const found = list.find(item => item.uuid === entity)
  return found ? found.nombre : entity
}

function getProveedorNombre(entity) {
  return getNombreEntidad(entity, proveedores.value)
}

function getClienteNombre(entity) {
  return getNombreEntidad(entity, clientes.value)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES')
}

function getDiasRestantes(fechaEntrega) {
  if (!fechaEntrega) return ''
  const hoy = new Date()
  const entrega = new Date(fechaEntrega)
  const diffTime = entrega - hoy
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

</script>

<style scoped>
.my-card {
  margin-bottom: 12px;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.my-card .q-card-section:last-child {
  flex: 1;
}
</style>