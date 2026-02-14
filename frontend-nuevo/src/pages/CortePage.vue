<template>
  <q-page class="q-pa-md q-gutter-sm">
    <div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div>
          <div class="row items-center q-mb-sm">
            <q-btn unelevated rounded icon="add" color="primary" @click="openDialog" label="Agregar Corte" />
            <q-space />
          </div>

          <q-table dense :rows="cortes" :columns="columns" row-key="uuid" flat >
            <template v-slot:body-cell-acciones="props">
              <q-td align="right">
                <q-btn dense flat icon="visibility" color="primary" @click.stop="openEdit(props.row)" v-ripple title="Ver / Editar" />
                <q-btn dense flat icon="edit" color="accent" @click.stop="openEdit(props.row)" v-ripple title="Editar" />
                <q-btn dense flat icon="delete" color="negative" @click.stop="deleteCorte(props.row.uuid)" v-ripple title="Eliminar" />
              </q-td>
            </template>
          </q-table>
        </div>
      </transition>

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
                  <q-input filled v-model="form.tercero" label="NOMBRE TERCERO" dense />
                </div>
                <div class="col-xs-6">
                  <q-input filled v-model="form.fecha" label="FECHA" dense type="date" />
                </div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-4"><q-input filled v-model="form.ref" label="REF" dense /></div>
                <div class="col-xs-4"><q-input filled v-model="form.tela" label="TELA" dense /></div>
                <div class="col-xs-4"><q-input filled v-model.number="form.mtrs_enviados" label="MTRS DE TELA ENVIADA" dense type="number" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-4"><q-input filled v-model="form.lote" label="LOTE" dense /></div>
                <div class="col-xs-8"><q-input filled v-model="form.orden_produccion" label="ORDEN DE PRODUCCION" dense /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Cortes (hasta 8 filas)</div>
              <div v-for="i in 8" :key="i" class="row q-col-gutter-md q-mt-sm items-center">
                <div class="col-xs-1">
                  <q-input dense v-model.number="detalles[i-1].numero" type="number" />
                </div>
                <div class="col-xs-2"><q-input dense v-model="detalles[i-1].proporcion" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].unidades_cortadas" type="number" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="detalles[i-1].ancho" type="number" /></div>
                <div class="col-xs-1"><q-input dense v-model.number="detalles[i-1].largo" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].promedio" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="detalles[i-1].mtrs_consumidos" type="number" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Tallas (S M L XL XXL)</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-2"><q-input dense v-model.number="tallas.s" label="S" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="tallas.m" label="M" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="tallas.l" label="L" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="tallas.xl" label="XL" type="number" /></div>
                <div class="col-xs-2"><q-input dense v-model.number="tallas.xxl" label="XXL" type="number" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Totales y consumo</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.total_unidades" label="Total unidades cortadas" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.total_metros_consumidos" label="Total metros consumidos" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.mtrs_retazos" label="Mtrs de retazos" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.promedio" label="Promedio" type="number" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.muestras" label="Muestras" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.faltante_tela" label="Faltante de tela" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.sobrante_tela" label="Sobrante de tela" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model="form.firma_responsable" label="Firma responsable" type="text" /></div>
              </div>

              <q-separator class="q-mt-md q-mb-md" />

              <div class="text-subtitle2">Consumo tela (de bolsillo / combinado)</div>
              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_cantidad" label="Cantidad" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_metros_gastados" label="Metros gastados" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_ancho" label="Ancho" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_largo" label="Largo" type="number" /></div>
              </div>

              <div class="row q-col-gutter-md q-mt-sm">
                <div class="col-xs-3"><q-input dense v-model.number="form.consumo_promedio" label="Promedio consumo" type="number" /></div>
                <div class="col-xs-3"><q-input dense v-model.number="form.faltante_tela" label="Faltante de tela" type="number" /></div>
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
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

const cortes = ref([])
const dialog = ref(false)
const editing = ref(false)
const editingUuid = ref(null)
const form = ref({
  tercero: '', fecha: '', ref: '', tela: '', mtrs_enviados: 0, lote: '', orden_produccion: '', notas: '',
  total_unidades: 0,
  total_metros_consumidos: 0,
  mtrs_retazos: 0,
  promedio: 0,
  muestras: 0,
  faltante_tela: 0,
  consumo_cantidad: 0,
  consumo_metros_gastados: 0,
  consumo_ancho: 0,
  consumo_largo: 0,
  consumo_promedio: 0,
  sobrante_tela: 0,
  firma_responsable: ''
})
const detalles = ref(Array.from({ length: 8 }).map((_, i) => ({ numero: i+1, proporcion: '', unidades_cortadas: 0, ancho: 0, largo: 0, promedio: 0, mtrs_consumidos: 0, color: '' })))
const tallas = ref({ s: 0, m: 0, l: 0, xl: 0, xxl: 0 })

const columns = [
  { name: 'tercero', label: 'Tercero', field: 'tercero' },
  { name: 'fecha', label: 'Fecha', field: 'fecha' },
  { name: 'ref', label: 'Ref', field: 'ref' },
  { name: 'tela', label: 'Tela', field: 'tela' },
  { name: 'acciones', label: 'Acciones', field: 'uuid' }
]

onMounted(() => {
  load()
})

async function load() {
  try {
    const r = await api.get('core/corte/')
    cortes.value = r.data
  } catch (err) {
    console.error(err)
  }
}

function openDialog() {
  editing.value = false
  editingUuid.value = null
  form.value = { tercero: '', fecha: '', ref: '', tela: '', mtrs_enviados: 0, lote: '', orden_produccion: '', notas: '',
    total_unidades: 0, total_metros_consumidos: 0, mtrs_retazos: 0, promedio: 0, muestras: 0, faltante_tela: 0,
    consumo_cantidad: 0, consumo_metros_gastados: 0, consumo_ancho: 0, consumo_largo: 0, consumo_promedio: 0, sobrante_tela: 0, firma_responsable: '' }
  detalles.value = Array.from({ length: 8 }).map((_, i) => ({ numero: i+1, proporcion: '', unidades_cortadas: 0, ancho: 0, largo: 0, promedio: 0, mtrs_consumidos: 0, color: '' }))
  tallas.value = { s: 0, m: 0, l: 0, xl: 0, xxl: 0 }
  dialog.value = true
}

function openEdit(row) {
  editing.value = true
  editingUuid.value = row.uuid
  // llenar form con datos del registro
  form.value = {
    tercero: row.tercero || '', fecha: row.fecha || '', ref: row.ref || '', tela: row.tela || '',
    mtrs_enviados: parseFloat(row.mtrs_enviados) || 0, lote: row.lote || '', orden_produccion: row.orden_produccion || '', notas: row.notas || '',
    total_unidades: row.total_unidades || 0, total_metros_consumidos: parseFloat(row.total_metros_consumidos) || 0,
    mtrs_retazos: parseFloat(row.mtrs_retazos) || 0, promedio: parseFloat(row.promedio) || 0, muestras: row.muestras || 0,
    faltante_tela: parseFloat(row.faltante_tela) || 0, consumo_cantidad: row.consumo_cantidad || 0,
    consumo_metros_gastados: parseFloat(row.consumo_metros_gastados) || 0, consumo_ancho: parseFloat(row.consumo_ancho) || 0,
    consumo_largo: parseFloat(row.consumo_largo) || 0, consumo_promedio: parseFloat(row.consumo_promedio) || 0,
    sobrante_tela: parseFloat(row.sobrante_tela) || 0, firma_responsable: row.firma_responsable || ''
  }

  // tallas -> intentar parsear JSON
  try {
    tallas.value = row.tallas ? JSON.parse(row.tallas) : { s: 0, m: 0, l: 0, xl: 0, xxl: 0 }
  } catch (e) {
    tallas.value = { s: 0, m: 0, l: 0, xl: 0, xxl: 0 }
  }

  // detalles: mapear los detalles recibidos en up to 8 filas
  const incoming = Array.isArray(row.detalles) ? row.detalles : []
  detalles.value = Array.from({ length: 8 }).map((_, i) => {
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

async function submit() {
  const payload = {
    ...form.value,
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
