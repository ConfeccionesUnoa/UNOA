<template>
  <q-page class="q-pa-md q-gutter-sm">
    <div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div>
          <div class="row items-center q-mb-sm">
            <q-btn unelevated rounded icon="add" color="primary" @click="openDialog" label="Agregar Corte" />
            <q-space />
          </div>

          <div class="row items-center q-mb-md">
            <q-input
              filled
              v-model="filterCorte"
              label="Buscar referencia"
              clearable
              dense
              debounce="300"
              style="max-width: 320px"
            />
          </div>

          <q-table dense :rows="filteredCortes" :columns="columns" row-key="uuid" flat >
            <template v-slot:body-cell-acciones="props">
              <q-td align="right">
                <q-btn dense flat icon="visibility" color="primary" @click.stop="openEdit(props.row)" v-ripple title="Ver / Editar" :disable="esCorteFinalizado(props.row)" />
                <q-btn dense flat icon="edit" color="accent" @click.stop="openEdit(props.row)" v-ripple title="Editar" :disable="esCorteFinalizado(props.row)" />
                <q-btn dense flat icon="play_circle" color="orange" @click.stop="openEstadoDialog(props.row)" v-ripple title="Avanzar proceso" :disable="esCorteFinalizado(props.row)" />
                <q-btn dense flat icon="picture_as_pdf" color="blue" @click.stop="openExportDialog(props.row)" v-ripple title="Exportar" />
                <q-btn dense flat icon="delete" color="negative" @click.stop="deleteCorte(props.row.uuid)" v-ripple title="Eliminar" :disable="esCorteFinalizado(props.row)" />
              </q-td>
            </template>
          </q-table>
        </div>
      </transition>

      <q-dialog v-model="estadoDialog" persistent>
        <q-card style="width: 400px; max-width: 90vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Seleccionar estado de Corte</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="estadoDialog=false" />
          </q-card-section>

          <q-card-section>
            <q-select
              filled
              v-model="estadoSeleccionado"
              :options="estadosCorte"
              label="Estado"
              emit-value
              map-options
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat color="negative" label="Cancelar" @click="estadoDialog=false" />
            <q-btn flat color="primary" label="Guardar" @click="confirmarEstado" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-dialog v-model="exportDialog" persistent>
        <q-card style="width: 450px; max-width: 90vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Exportar Corte</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="exportDialog=false" />
          </q-card-section>

          <q-card-section>
            <div class="q-mt-sm q-mb-sm">Elige modo de exportación:</div>
            <q-btn label="Completo" color="primary" class="q-mr-sm" @click="exportCorte('completo')" />
            <q-btn label="Maquila" color="secondary" @click="exportCorte('maquila')" />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat color="primary" label="Cerrar" @click="exportDialog=false" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-dialog v-model="dialog" persistent>
        <q-card style="width: 900px; max-width: 95vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Crear Informe de Corte</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="dialog=false" />
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="submit">
              <div class="row q-col-gutter-md">
                <div class="col-xs-6">
                  <q-select
                    filled
                    v-model="programacionSeleccionada"
                    :options="programacionesDisponibles"
                    option-label="numero_orden"
                    option-value="uuid"
                    label="Referencia"
                    dense
                    emit-value
                    map-options
                    @update:model-value="(prog) => { console.log('q-select update prog:', prog); cargarProgramacionSeleccionada(prog); }"
                  />
                </div>
                <div class="col-xs-6">
                  <q-input filled v-model="form.fecha" label="FECHA" dense type="date" />
                </div>
              </div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-6">
                  <q-input filled v-model="form.tercero" label="NOMBRE TERCERO" dense />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-6"><q-input filled v-model="form.tela" label="TELA" dense /></div>
                <div class="col-xs-6"><q-input filled v-model.number="form.mtrs_enviados" label="MTRS DE TELA ENVIADA" dense type="number" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-4"><q-input filled v-model="form.lote" label="LOTE" dense /></div>
                <div class="col-xs-8"><q-input filled v-model="form.orden_produccion" label="ORDEN DE PRODUCCION" dense /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Cortes (hasta 10 filas)</div>
              <!-- Headers -->
              <div class="row q-col-gutter-md q-mt-sm text-weight-bold bg-grey-2 q-pa-sm" style="border-bottom: 2px solid #ccc;">
                <div class="col-xs-1" style="text-align: center;">CORTE</div>
                <div class="col-xs-2" style="text-align: center;">PROPORCION</div>
                <div class="col-xs-2" style="text-align: center;">UNID CORTADAS</div>
                <div class="col-xs-1" style="text-align: center;">ANCHO</div>
                <div class="col-xs-1" style="text-align: center;">LARGO</div>
                <div class="col-xs-2" style="text-align: center;">PROMEDIO</div>
                <div class="col-xs-2" style="text-align: center;">MTRS CONSUMIDOS</div>
              </div>
              <!-- Data rows -->
              <div v-for="i in 10" :key="i" class="row q-col-gutter-md q-mt-sm items-center">
                <div class="col-xs-1">
                  <q-input dense v-model.number="detalles[i-1].numero" type="number" />
                </div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].proporcion" type="number" @update:model-value="calculateMetrics(i-1)" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].unidades_cortadas" type="number" @update:model-value="calculateMetrics(i-1)" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="detalles[i-1].ancho" type="number" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="detalles[i-1].largo" type="number" @update:model-value="calculateMetrics(i-1)" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].promedio" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].mtrs_consumidos" type="number" readonly class="bg-grey-2" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Total unidades cortadas - Tallas</div>
              <div class="text-caption q-mb-sm">Tallas en letras (S, M, L, XL, XXL)</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-1"><q-input dense v-model.number="tallas.s" label="S" type="number" @update:model-value="calculateTallaTotal" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="tallas.m" label="M" type="number" @update:model-value="calculateTallaTotal" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="tallas.l" label="L" type="number" @update:model-value="calculateTallaTotal" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="tallas.xl" label="XL" type="number" @update:model-value="calculateTallaTotal" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="tallas.xxl" label="XXL" type="number" @update:model-value="calculateTallaTotal" /></div>
              </div>

              <div class="text-caption q-mt-md q-mb-sm">Tallas numéricas (4 - 46)</div>
              <div class="row q-col-gutter-md q-mt-sm">
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
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
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

              <div class="row q-col-gutter-md q-mt-md">
                <div class="col-xs-2"><q-input dense v-model.number="tallas.total" label="TOTAL TALLAS" type="number" readonly class="bg-grey-2 text-weight-bold" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Totales y consumo</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.total_unidades" label="Total unidades cortadas" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.total_metros_consumidos" label="Total metros consumidos" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.mtrs_retazos" label="Mtrs de retazos" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.promedio" label="Promedio" type="number" readonly class="bg-grey-2" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.muestras" label="Muestras" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.faltante_tela" label="Faltante de tela" type="number" @update:model-value="actualizarCalculosAutomaticos" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.sobrante_tela" label="Sobrante de tela" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-3"><q-input dense v-model="form.firma_responsable" label="Firma responsable" type="text" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Consumo tela (de bolsillo / combinado)</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_cantidad" label="Cantidad" type="number" @update:model-value="actualizarCalculosAutomaticos" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_metros_gastados" label="Metros gastados" type="number" readonly class="bg-grey-2" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_ancho" label="Ancho" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_largo" label="Largo" type="number" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_promedio" label="Promedio consumo" type="number" @update:model-value="actualizarCalculosAutomaticos" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="consumoData.faltante_tela" label="Faltante de tela" type="number" @update:model-value="actualizarCalculosAutomaticos" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="consumoData.sobrante_tela" label="Sobrante de tela" type="number" readonly class="bg-grey-2" /></div>
              </div>

              <q-card-actions align="right">
                <q-btn label="Cancelar" v-close-popup color="negative" flat @click="dialog=false" />
                <q-btn label="Guardar" color="primary" @click="submit" />
              </q-card-actions>
            </q-form>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

const cortes = ref([])
const presentaciones = ref([])
const dialog = ref(false)
const editing = ref(false)
const editingUuid = ref(null)
const programacionesActivas = ref([])
const programacionSeleccionada = ref(null)
const estadoDialog = ref(false)
const estadoSeleccionado = ref('')
const filterCorte = ref('')
const corteSeleccionado = ref(null)
const exportDialog = ref(false)
const corteParaExportar = ref(null)
const form = ref({
  tercero: '', fecha: '', tela: '', mtrs_enviados: 0, lote: '', orden_produccion: '', notas: '',
  total_unidades: 0,
  total_metros_consumidos: 0,
  mtrs_retazos: 0,
  promedio: 0,
  muestras: 0,
  faltante_tela: 0,
  sobrante_tela: 0,
  consumo_cantidad: 0,
  consumo_metros_gastados: 0,
  consumo_ancho: 0,
  consumo_largo: 0,
  consumo_promedio: 0,
  firma_responsable: ''
})
const consumoData = ref({
  faltante_tela: 0,
  sobrante_tela: 0
})
const detalles = ref(Array.from({ length: 10 }).map((_, i) => ({ numero: i+1, proporcion: '', unidades_cortadas: 0, ancho: 0, largo: 0, promedio: 0, mtrs_consumidos: 0, color: '' })))
const tallas = ref({
  s: 0, m: 0, l: 0, xl: 0, xxl: 0,
  t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0,
  total: 0
})

const estadosCorte = ref([
  'ESTANTERIA',
  'PREPARACION',
  'ENSAMBLE',
  'FIN_PUNTAS',
  'PRESILLA',
  'TERMINADO'
])


const columns = [
  { name: 'referencia', label: 'Referencia', field: row => row.orden_produccion || row.referencia || '' },
  { name: 'tercero', label: 'Tercero', field: 'tercero' },
  { name: 'fecha', label: 'Fecha', field: 'fecha' },
  { name: 'tela', label: 'Tela', field: 'tela' },
  { name: 'estado', label: 'Estado', field: 'estado' },
  { name: 'fecha_estado', label: 'Fecha Estado', field: 'fecha_estado' },
  { name: 'acciones', label: 'Acciones', field: 'uuid' }
]

const programacionesFinalizadas = computed(() => {
  const finalizados = new Set(
    presentaciones.value
      .filter(p => p.estado_proceso === 'FIN')
      .map(p => p.referencia)
      .filter(Boolean)
  )
  return finalizados
})

const programacionesDisponibles = computed(() => {
  return programacionesActivas.value.filter(p => !programacionesFinalizadas.value.has(p.numero_orden))
})

const filteredCortes = computed(() => {
  const query = (filterCorte.value || '').toString().trim().toLowerCase()
  let list = cortes.value
  if (!query) return list
  return list.filter(corte => {
    const referencia = (corte.orden_produccion || corte.referencia || '').toString().toLowerCase()
    return referencia.includes(query)
  })
})

onMounted(() => {
  console.log('onMounted called')
  load()
  loadProgramacionesActivas()
  loadPresentaciones()
})

watch(
  () => [
    form.value.mtrs_enviados,
    form.value.faltante_tela,
    form.value.consumo_promedio,
    form.value.consumo_metros_gastados,
    form.value.consumo_cantidad,
    form.value.total_unidades,
    form.value.total_metros_consumidos,
    consumoData.value.faltante_tela
  ],
  () => {
    actualizarCalculosAutomaticos()
  },
  { deep: true }
)

async function load() {
  try {
    const r = await api.get('core/corte/')
    cortes.value = r.data
  } catch (err) {
    console.error(err)
  }
}

async function loadProgramacionesActivas() {
  try {
    const r = await api.get('core/programacion/')
    programacionesActivas.value = r.data
    console.log('programacionesActivas loaded:', programacionesActivas.value)
  } catch (err) {
    console.error('Error loading programaciones:', err)
  }
}

async function loadPresentaciones() {
  try {
    const r = await api.get('core/presentacion/')
    presentaciones.value = r.data
    console.log('presentaciones loaded:', presentaciones.value)
  } catch (err) {
    console.error('Error loading presentaciones:', err)
  }
}

function openDialog() {
  editing.value = false
  editingUuid.value = null
  programacionSeleccionada.value = null
  form.value = { tercero: '', fecha: '', tela: '', mtrs_enviados: 0, lote: '', orden_produccion: '', notas: '',
    total_unidades: 0, total_metros_consumidos: 0, mtrs_retazos: 0, promedio: 0, muestras: 0, faltante_tela: 0, sobrante_tela: 0,
    consumo_cantidad: 0, consumo_metros_gastados: 0, consumo_ancho: 0, consumo_largo: 0, consumo_promedio: 0, firma_responsable: '',
    estado: 'RECIBO', fecha_estado: new Date().toISOString().split('T')[0] }
  consumoData.value = { faltante_tela: 0, sobrante_tela: 0 }
  detalles.value = Array.from({ length: 10 }).map((_, i) => ({ numero: i+1, proporcion: '', unidades_cortadas: 0, ancho: 0, largo: 0, promedio: 0, mtrs_consumidos: 0, color: '' }))
  tallas.value = { s: 0, m: 0, l: 0, xl: 0, xxl: 0, t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0, total: 0 }
  dialog.value = true
}

function openEdit(row) {
  editing.value = true
  editingUuid.value = row.uuid
  // llenar form con datos del registro
  form.value = {
    tercero: row.tercero || '', fecha: row.fecha || '', tela: row.tela || '',
    mtrs_enviados: parseFloat(row.mtrs_enviados) || 0, lote: row.lote || '', orden_produccion: row.orden_produccion || '', notas: row.notas || '',
    total_unidades: row.total_unidades || 0, total_metros_consumidos: parseFloat(row.total_metros_consumidos) || 0,
    mtrs_retazos: parseFloat(row.mtrs_retazos) || 0, promedio: parseFloat(row.promedio) || 0, muestras: row.muestras || 0,
    faltante_tela: parseFloat(row.faltante_tela) || 0, consumo_cantidad: row.consumo_cantidad || 0,
    consumo_metros_gastados: parseFloat(row.consumo_metros_gastados) || 0, consumo_ancho: parseFloat(row.consumo_ancho) || 0,
    consumo_largo: parseFloat(row.consumo_largo) || 0, consumo_promedio: parseFloat(row.consumo_promedio) || 0,
    sobrante_tela: parseFloat(row.sobrante_tela) || 0, firma_responsable: row.firma_responsable || '',
    estado: row.estado || 'RECIBO', fecha_estado: row.fecha_estado || ''
  }

  // tallas -> intentar parsear JSON
  try {
    tallas.value = row.tallas ? JSON.parse(row.tallas) : { s: 0, m: 0, l: 0, xl: 0, xxl: 0, t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0, total: 0 }
  } catch (e) {
    tallas.value = { s: 0, m: 0, l: 0, xl: 0, xxl: 0, t4: 0, t6: 0, t8: 0, t10: 0, t12: 0, t14: 0, t16: 0, t18: 0, t20: 0, t22: 0, t26: 0, t28: 0, t30: 0, t32: 0, t34: 0, t36: 0, t38: 0, t40: 0, t42: 0, t44: 0, t46: 0, total: 0 }
  }
  calculateTallaTotal()
  actualizarTotalesDetalle()

  // detalles: mapear los detalles recibidos en up to 8 filas
  const incoming = Array.isArray(row.detalles) ? row.detalles : []
  detalles.value = Array.from({ length: 10 }).map((_, i) => {
    const d = incoming[i]
    if (d) {
      return {
        numero: d.numero || i+1,
        proporcion: d.proporcion || '',
        unidades_cortadas: d.unidades_cortadas || 0,
        ancho: parseFloat(d.ancho) || 0,
        largo: parseFloat(d.largo) || 0,
        promedio: parseFloat(d.promedio) || 0,
        mtrs_consumidos: parseFloat(d.mtrs_consumidos) || 0,
        color: d.color || ''
      }
    }
    return { numero: i+1, proporcion: '', unidades_cortadas: 0, ancho: 0, largo: 0, promedio: 0, mtrs_consumidos: 0, color: '' }
  })
  
  // Cargar datos de consumo al editar
  consumoData.value = {
    faltante_tela: 0,
    sobrante_tela: 0
  }

  dialog.value = true
}

async function deleteCorte(uuid) {
  const res = await Swal.fire({
    title: 'Confirmar eliminación',
    text: '¿Eliminar este corte?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  })
  if (!res.isConfirmed) return
  try {
    await api.delete(`core/corte/${uuid}/`)
    Swal.fire('Eliminado', 'Corte eliminado', 'success')
    await load()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', err?.response?.data?.detail || 'No se pudo eliminar', 'error')
  }
}

function calculateMetrics(index) {
  const detalle = detalles.value[index]
  // promedio = (largo / proporcion) * 2
  if (detalle.proporcion && detalle.largo) {
    detalle.promedio = (detalle.largo / detalle.proporcion) * 2
  }
  // mtrs_consumidos = promedio * unidades_cortadas
  if (detalle.promedio && detalle.unidades_cortadas) {
    detalle.mtrs_consumidos = detalle.promedio * detalle.unidades_cortadas
  }
  actualizarTotalesDetalle()
}

function calculateTallaTotal() {
  tallas.value.total = (tallas.value.s || 0) + (tallas.value.m || 0) + (tallas.value.l || 0) + (tallas.value.xl || 0) + (tallas.value.xxl || 0) +
    (tallas.value.t4 || 0) + (tallas.value.t6 || 0) + (tallas.value.t8 || 0) + (tallas.value.t10 || 0) + (tallas.value.t12 || 0) +
    (tallas.value.t14 || 0) + (tallas.value.t16 || 0) + (tallas.value.t18 || 0) + (tallas.value.t20 || 0) + (tallas.value.t22 || 0) +
    (tallas.value.t26 || 0) + (tallas.value.t28 || 0) + (tallas.value.t30 || 0) + (tallas.value.t32 || 0) + (tallas.value.t34 || 0) +
    (tallas.value.t36 || 0) + (tallas.value.t38 || 0) + (tallas.value.t40 || 0) + (tallas.value.t42 || 0) + (tallas.value.t44 || 0) +
    (tallas.value.t46 || 0)
  // si la selección de ref trae tallas, también setear totales en form (opcional)
  form.value.total_unidades = detalles.value.reduce((sum, d) => sum + (Number(d.unidades_cortadas) || 0), 0)
  form.value.total_metros_consumidos = detalles.value.reduce((sum, d) => sum + (Number(d.mtrs_consumidos) || 0), 0)
  actualizarCalculosAutomaticos()
}

function actualizarCalculosAutomaticos() {
  // ========== SECCIÓN: Totales y consumo ==========
  // Promedio: total metros consumidos / total unidades cortadas
  if (form.value.total_unidades > 0) {
    form.value.promedio = Number((form.value.total_metros_consumidos / form.value.total_unidades).toFixed(3))
  } else {
    form.value.promedio = 0
  }

  // Sobrante de tela (sección principal): mtrs enviados - total metros consumidos - faltante de tela
  form.value.sobrante_tela = Number((form.value.mtrs_enviados - form.value.total_metros_consumidos - form.value.faltante_tela).toFixed(3))

  // Mtrs retazos: mtrs enviados - total metros consumidos - faltante de tela (IGUAL al sobrante_tela de la sección principal)
  form.value.mtrs_retazos = form.value.sobrante_tela

  // ========== SECCIÓN: Consumo tela (de bolsillo) ==========
  // Metros gastados: promedio consumo * total unidades cortadas
  form.value.consumo_metros_gastados = Number((form.value.consumo_promedio * form.value.total_unidades).toFixed(3))

  // Sobrante de tela (sección consumo): cantidad - metros gastados - faltante de tela consumo
  consumoData.value.sobrante_tela = Number((form.value.consumo_cantidad - form.value.consumo_metros_gastados - consumoData.value.faltante_tela).toFixed(3))
}

function nextState(current) {
  const cadena = ['ESTANTERIA', 'PREPARACION', 'ENSAMBLE', 'FIN_PUNTAS', 'PRESILLA', 'TERMINADO']
  if (!current) return cadena[0]
  const idx = cadena.indexOf(current)
  if (idx === -1 || idx === cadena.length - 1) return current || cadena[0]
  return cadena[idx + 1]
}

function cargarProgramacionSeleccionada(prog) {
  console.log('cargarProgramacionSeleccionada called with prog:', prog)
  if (!prog) {
    console.log('no prog')
    return
  }

  let programa = null
  if (typeof prog === 'string') {
    programa = programacionesActivas.value.find(p => p.uuid === prog) || programacionesDisponibles.value.find(p => p.uuid === prog)
  } else {
    programa = prog
  }

  if (!programa) {
    console.warn('Programación seleccionada no encontrada:', prog)
    return
  }

  if (programacionesFinalizadas.value.has(programa.numero_orden)) {
    Swal.fire('Atención', 'Esta referencia está finalizada y no se puede usar.', 'warning')
    programacionSeleccionada.value = null
    return
  }

  // cargar tallas programadas
  console.log('tallas from prog:', programa.tallas)
  try {
    const t = programa.tallas ? JSON.parse(programa.tallas) : {}
    console.log('parsed tallas:', t)
    tallas.value = {
      s: t.s || 0, m: t.m || 0, l: t.l || 0, xl: t.xl || 0, xxl: t.xxl || 0,
      t4: t.t4 || 0, t6: t.t6 || 0, t8: t.t8 || 0, t10: t.t10 || 0, t12: t.t12 || 0,
      t14: t.t14 || 0, t16: t.t16 || 0, t18: t.t18 || 0, t20: t.t20 || 0, t22: t.t22 || 0,
      t26: t.t26 || 0, t28: t.t28 || 0, t30: t.t30 || 0, t32: t.t32 || 0, t34: t.t34 || 0,
      t36: t.t36 || 0, t38: t.t38 || 0, t40: t.t40 || 0, t42: t.t42 || 0, t44: t.t44 || 0,
      t46: t.t46 || 0, total: t.total || 0
    }
    console.log('tallas.value set to:', tallas.value)
    calculateTallaTotal()
  } catch (e) {
    console.error('tallas inválidas en programación', e)
  }

  form.value.orden_produccion = programa.numero_orden || ''
  console.log('orden_produccion set to:', form.value.orden_produccion)
}


function openEstadoDialog(corte) {
  if (esCorteFinalizado(corte)) {
    Swal.fire('Atención', 'No se puede cambiar estado de un corte cuya referencia está finalizada.', 'warning')
    return
  }
  corteSeleccionado.value = corte
  estadoSeleccionado.value = corte.estado || estadosCorte.value[0] || 'RECIBO'
  estadoDialog.value = true
}

function esCorteFinalizado(corte) {
  const orden = (corte.orden_produccion || corte.referencia || '').toString()
  return programacionesFinalizadas.value.has(orden)
}

async function confirmarEstado() {
  if (!corteSeleccionado.value) return
  const nuevoEstado = estadoSeleccionado.value
  const hoy = new Date().toISOString().split('T')[0]
  try {
    await api.patch(`core/corte/${corteSeleccionado.value.uuid}/`, { estado: nuevoEstado, fecha_estado: hoy })
    estadoDialog.value = false
    await load()
    Swal.fire('Actualizado', `Estado cambiado a ${nuevoEstado}`, 'success')
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo actualizar el estado', 'error')
  }
}

function openExportDialog(corte) {
  corteParaExportar.value = corte
  exportDialog.value = true
}

function exportCorte(mode) {
  if (!corteParaExportar.value) return
  const corte = corteParaExportar.value
  const tallasData = (() => {
    try {
      return corte.tallas ? JSON.parse(corte.tallas) : {}
    } catch (e) {
      return {}
    }
  })()

  const buildTallasTable = () => {
    const cols = ['s', 'm', 'l', 'xl', 'xxl', 't4', 't6', 't8', 't10', 't12', 't14', 't16', 't18', 't20', 't22', 't26', 't28', 't30', 't32', 't34', 't36', 't38', 't40', 't42', 't44', 't46']
    const rows = cols.map(k => `<tr><td>${k.toUpperCase()}</td><td>${tallasData[k] || 0}</td></tr>`).join('')
    return `<table class="pdf-table"><thead><tr><th>Talla</th><th>Cantidad</th></tr></thead><tbody>${rows}<tr><td><strong>TOTAL</strong></td><td><strong>${tallasData.total || 0}</strong></td></tr></tbody></table>`
  }

  const buildDetalleCorteTable = () => {
    if (!corte.detalles || !corte.detalles.length) {
      return '<div>No hay detalles de corte</div>'
    }
    const rows = corte.detalles.map(d => `<tr><td>${d.numero || ''}</td><td>${d.proporcion || ''}</td><td>${d.unidades_cortadas || 0}</td><td>${d.ancho || 0}</td><td>${d.largo || 0}</td><td>${d.promedio || 0}</td><td>${d.mtrs_consumidos || 0}</td></tr>`).join('')
    return `<table class="pdf-table"><thead><tr><th>Cor</th><th>Prop</th><th>Unid</th><th>An</th><th>L</th><th>Prom</th><th>Mtrs</th></tr></thead><tbody>${rows}</tbody></table>`
  }

  const buildHeaderHtml = () => `
    <div class="section">
      <h1>Corte</h1>
      <div class="grid">
        <div class="field"><strong>UUID:</strong> ${corte.uuid || ''}</div>
        <div class="field"><strong>Fecha:</strong> ${corte.fecha || ''}</div>
        <div class="field"><strong>Tercero:</strong> ${corte.tercero || ''}</div>
        <div class="field"><strong>Tela:</strong> ${corte.tela || ''}</div>
        <div class="field"><strong>Mtrs Enviados:</strong> ${corte.mtrs_enviados || 0}</div>
        <div class="field"><strong>Lote:</strong> ${corte.lote || ''}</div>
        <div class="field"><strong>Orden Prod:</strong> ${corte.orden_produccion || ''}</div>
        <div class="field"><strong>Notas:</strong> ${corte.notas || ''}</div>
        <div class="field"><strong>Estado:</strong> ${corte.estado || ''}</div>
        <div class="field"><strong>Fecha Estado:</strong> ${corte.fecha_estado || ''}</div>
      </div>
    </div>`

  const buildTotalsHtml = () => `
    <div class="section">
      <h2>Totales y Consumo</h2>
      <div class="grid">
        <div class="field"><strong>Total unidades cortadas:</strong> ${corte.total_unidades || 0}</div>
        <div class="field"><strong>Total mtrs consumidos:</strong> ${corte.total_metros_consumidos || 0}</div>
        <div class="field"><strong>Mtrs retazos:</strong> ${corte.mtrs_retazos || 0}</div>
        <div class="field"><strong>Promedio:</strong> ${corte.promedio || 0}</div>
        <div class="field"><strong>Muestras:</strong> ${corte.muestras || 0}</div>
        <div class="field"><strong>Faltante tela:</strong> ${corte.faltante_tela || 0}</div>
        <div class="field"><strong>Sobrante tela:</strong> ${corte.sobrante_tela || 0}</div>
        <div class="field"><strong>Consumo cantidad:</strong> ${corte.consumo_cantidad || 0}</div>
        <div class="field"><strong>Consumo mtrs gastados:</strong> ${corte.consumo_metros_gastados || 0}</div>
        <div class="field"><strong>Consumo promedio:</strong> ${corte.consumo_promedio || 0}</div>
        <div class="field"><strong>Firma:</strong> ${corte.firma_responsable || ''}</div>
      </div>
    </div>`

  let html = `
    <style>
      body { font-family: Arial, sans-serif; margin: 16px; color: #202020; }
      h1 { font-size: 22px; margin-bottom: 8px; }
      h2 { font-size: 18px; margin-bottom: 8px; margin-top: 18px; }
      .section { margin-bottom: 14px; }
      .grid { display: flex; flex-wrap: wrap; gap: 10px; }
      .field { width: calc(50% - 10px); }
      .pdf-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
      .pdf-table th, .pdf-table td { border: 1px solid #999; padding: 6px 8px; text-align: center; }
      .pdf-table thead { background: #f0f0f0; }
    </style>
    ${buildHeaderHtml()}
    <div class="section"><h2>Tallas</h2>${buildTallasTable()}</div>
  `

  if (mode === 'maquila') {
    html += `${buildTotalsHtml()}<div class="section"><h2>Detalles</h2>${buildDetalleCorteTable()}</div>`
  }

  const w = window.open('', '_blank')
  if (w) {
    w.document.write(`<html><head><title>Export Corte</title></head><body>${html}</body></html>`)
    w.document.close()
    w.focus()
    setTimeout(() => w.print(), 300)
  } else {
    Swal.fire('Error', 'No se pudo abrir ventana de impresión', 'error')
  }

  exportDialog.value = false
}

function actualizarTotalesDetalle() {
  form.value.total_unidades = detalles.value.reduce((sum, d) => sum + (Number(d.unidades_cortadas) || 0), 0)
  form.value.total_metros_consumidos = detalles.value.reduce((sum, d) => sum + (Number(d.mtrs_consumidos) || 0), 0)
  actualizarCalculosAutomaticos()
}

async function submit() {
  actualizarCalculosAutomaticos()
  const payload = {
    ...form.value,
    sobrante_tela: consumoData.value.sobrante_tela,
    tallas: JSON.stringify(tallas.value),
    detalles_input: detalles.value.filter(d => d.unidades_cortadas || d.mtrs_consumidos || d.proporcion)
  }
  try {
    if (editing.value && editingUuid.value) {
      await api.put(`core/corte/${editingUuid.value}/`, payload)
    } else {
      await api.post('core/corte/', payload)
    }
    dialog.value = false
    Swal.fire('Éxito', 'Corte creado', 'success')
    await load()
  } catch (err) {
    console.error(err)
    Swal.fire('Error', err?.response?.data?.detail || 'No se pudo crear', 'error')
  }
}
</script>

<style scoped>
</style>
