<template>
    <q-page class="q-pa-md q-gutter-sm">
        <div>
            <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
                <div>
                    <q-space />

                    <q-table dense :rows="data" :columns="columns" :loading="visible"
                        :loading-label="visible ? 'Cargando...' : ''" rows-per-page-label="Filas por página"
                        :no-data-label="visible ? 'No hay datos' : ''"
                        :no-results-label="visible ? 'No hay resultados' : ''"
                        :rows-per-page-options="[10, 15, 20, 25, 50, 0]" v-model:pagination="pagination"
                        title="Inventario" :filter="filter" row-key="uuid">

                        <template v-slot:top-left>
                            <Can I="create" an="Inventario">
                                <q-btn unelevated rounded icon="add" color="primary" @click="creating"
                                    label="Agregar" />
                                <q-space />
                            </Can>
                        </template>

                        <template v-slot:top-right>
                            <q-input dense debounce="300" v-model="filter" placeholder="Buscar">
                                <template v-slot:append>
                                    <q-icon name="search" />
                                </template>
                            </q-input>
                        </template>

                        <template v-slot:body="props">
                            <q-tr :props="props">
                                <q-td key="codigo" :props="props">
                                    {{ props.row.codigo }}
                                </q-td>

                                <q-td key="nombre" :props="props">
                                    {{ props.row.nombre }}
                                </q-td>

                                <q-td key="descripcion" :props="props">
                                    {{ props.row.descripcion }}
                                </q-td>

                                <q-td key="observaciones" :props="props">
                                    {{ props.row.observaciones }}
                                </q-td>

                                <q-td key="proveedor" :props="props">
                                    {{ props.row.proveedor ? props.row.proveedor.nombre : '-' }}
                                </q-td>

                                <q-td key="cantidad" :props="props">
                                    {{ props.row.cantidad }}
                                </q-td>

                                <q-td key="valor_ingreso" :props="props">
                                    {{ formatCurrency(props.row.valor_ingreso) }}
                                </q-td>

                                <q-td key="numero_factura" :props="props">
                                    {{ props.row.numero_factura || '-' }}
                                </q-td>

                                <q-td key="fecha" :props="props">
                                    {{ props.row.fecha || '-' }}
                                </q-td>

                                <q-td key="precio_unitario" :props="props">
                                    {{ formatCurrency(props.row.precio_unitario) }}
                                </q-td>

                                <q-td key="valor_total" :props="props">
                                    {{ formatCurrency(props.row.valor_total) }}
                                </q-td>

                                <q-td key="categoria" :props="props">
                                    {{ props.row.categoria }}
                                </q-td>

                                <q-td key="estado" :props="props">
                                    <q-badge :color="props.row.estado === 'AC' ? 'green' : 'red'">
                                        {{ props.row.estado === 'AC' ? 'Activo' : 'Inactivo' }}
                                    </q-badge>
                                </q-td>

                                <Can I="update" an="Inventario">
                                    <q-td key="agregar" :props="props">
                                        <q-btn round size="xs" color="cyan-8" icon="add_shopping_cart"
                                            v-on:click="openIngreso(props.row)" />
                                    </q-td>
                                </Can>

                                <Can I="update" an="Inventario">
                                    <q-td key="edit" :props="props">
                                        <q-btn round size="xs" color="primary" icon="border_color"
                                            v-on:click="editing(props.row)" />
                                    </q-td>
                                </Can>

                                <Can I="delete" an="Inventario">
                                    <q-td key="delete" :props="props">
                                        <q-btn round size="xs" color="negative" icon="delete_forever"
                                            v-on:click="onDelete(props.row)" />
                                    </q-td>
                                </Can>
                            </q-tr>
                        </template>
                    </q-table>
                </div>
            </transition>

            <q-inner-loading :showing="visible">
                <q-spinner-pie color="primary" size="70px" />
            </q-inner-loading>

            <div class="row q-mt-md q-pt-sm">
                <q-space />
                <q-btn label="Descargar Excel" :disable="visible" icon="file_download" color="primary" @click="downloadExcel" />
            </div>
        </div>

        <q-dialog v-model="toolbar" persistent>
            <q-card style="width: 900px; max-width: 95vw;">
                <q-card-section class="row items-center q-pb-none">
                    <div class="text-h6">{{ isEditing ? 'Editar Producto' : 'Nuevo Producto de Inventario' }}</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-linear-progress :value="1" color="primary" />

                <q-card-section class="q-pt-md">
                    <q-form ref="form_ref" @submit.prevent="onSubmit" class="q-gutter-md">
                        <!-- SECCIÓN 1: INFORMACIÓN BÁSICA -->
                        <div class="section-title">Información Básica</div>
                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="codigo" label="Código *" lazy-rules dense
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="nombre" label="Nombre *" lazy-rules dense
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12">
                                <q-input filled v-model="descripcion" label="Descripción" type="textarea"
                                    rows="2" dense counter maxlength="500" />
                            </div>
                        </div>

                        <!-- SECCIÓN 2: PROVEEDOR Y DATOS DE ENTRADA -->
                        <div class="section-title q-mt-md">Datos del Proveedor</div>
                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-select filled v-model="proveedor" :options="proveedores" option-value="uuid" 
                                    option-label="nombre" label="Proveedor" emit-value map-options dense />
                            </div>
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="numero_factura" label="Número de factura" dense />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="fecha" label="Fecha" type="date" dense />
                            </div>
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model.number="valor_ingreso" label="Valor de Ingreso" 
                                    type="number" step="0.01" min="0" dense prefix="$" />
                            </div>
                        </div>

                        <!-- SECCIÓN 3: INVENTARIO Y PRECIOS -->
                        <div class="section-title q-mt-md">Información de Inventario</div>
                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-4">
                                <q-input filled v-model.number="cantidad" label="Cantidad *" type="number"
                                    min="0" dense lazy-rules
                                    :rules="[val => val >= 0 || 'La cantidad debe ser >= 0']" />
                            </div>
                            <div class="col-xs-12 col-sm-4">
                                <q-input filled v-model.number="precio_unitario" label="Precio Unitario *"
                                    type="number" step="0.01" min="0" dense lazy-rules prefix="$"
                                    :rules="[val => val >= 0 || 'El precio debe ser >= 0']" />
                            </div>
                            <div class="col-xs-12 col-sm-4">
                                <q-select filled v-model="categoria" :options="categoriaOptions" option-value="value" option-label="label" label="Categoría *" lazy-rules dense
                                    emit-value map-options
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>

                        <!-- SECCIÓN 4: OBSERVACIONES Y ESTADO -->
                        <div class="section-title q-mt-md">Detalles Adicionales</div>
                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12">
                                <q-input filled v-model="observaciones" label="Observaciones" type="textarea" 
                                    rows="2" dense counter maxlength="500" />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-select filled v-model="estado" :options="estadoOptions" option-value="value"
                                    option-label="label" label="Estado *" lazy-rules dense
                                    :rules="[val => !!val || 'El campo es obligatorio']" />
                            </div>
                        </div>
                    </q-form>
                </q-card-section>

                <q-separator />

                <q-card-actions align="right" class="q-pa-md">
                    <q-btn label="Cancelar" v-close-popup color="negative" flat />
                    <q-btn v-if="!isEditing" label="Guardar Producto" @click.prevent="onSubmit" color="primary" />
                    <q-btn v-else label="Actualizar Producto" @click.prevent="onEdit" color="primary" />
                </q-card-actions>

            </q-card>
        </q-dialog>

        <q-dialog v-model="ingresoToolbar" persistent>
            <q-card style="width: 600px; max-width: 95vw;">
                <q-card-section class="row items-center q-pb-none">
                    <div class="text-h6">Registrar Ingreso de Inventario</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-linear-progress :value="1" color="secondary" />

                <q-card-section class="q-pt-md">
                    <q-form ref="form_ingreso_ref" @submit.prevent="onSubmitIngreso" class="q-gutter-md">
                        
                        <!-- INFORMACIÓN ACTUAL DEL PRODUCTO -->
                        <div class="info-box">
                            <div class="text-subtitle2 text-weight-medium q-mb-sm">Estado Actual del Inventario</div>
                            <div class="row q-col-gutter-md">
                                <div class="col-xs-6">
                                    <div class="text-caption text-grey">Disponibilidad</div>
                                    <div class="text-h6">{{ ingresoDisponibilidad }}</div>
                                </div>
                            </div>
                        </div>

                        <q-separator />

                        <!-- DATOS DEL INGRESO -->
                        <div class="section-title">Datos del Ingreso</div>
                        
                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model.number="ingresoCantidad" label="Cantidad a agregar *" 
                                    type="number" min="1" dense lazy-rules 
                                    :rules="[val => val > 0 || 'La cantidad debe ser mayor a 0']" />
                            </div>
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="ingresoFecha" label="Fecha *" type="date" dense 
                                    lazy-rules :rules="[val => !!val || 'La fecha es requerida']" />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model="ingresoNumeroFactura" label="Número de factura" dense />
                            </div>
                            <div class="col-xs-12 col-sm-6">
                                <q-input filled v-model.number="ingresoValorIngreso" label="Valor de ingreso" 
                                    type="number" step="0.01" min="0" dense prefix="$" />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12">
                                <q-select filled v-model="ingresoProveedor" :options="proveedores" 
                                    option-value="uuid" option-label="nombre" label="Proveedor" 
                                    emit-value map-options dense />
                            </div>
                        </div>

                        <div class="row q-col-gutter-md">
                            <div class="col-xs-12">
                                <q-input filled v-model="ingresoObservaciones" label="Observaciones" 
                                    type="textarea" rows="2" dense counter maxlength="300" />
                            </div>
                        </div>

                    </q-form>
                </q-card-section>

                <q-separator />

                <q-card-actions align="right" class="q-pa-md">
                    <q-btn label="Cancelar" v-close-popup color="negative" flat />
                    <q-btn label="Registrar Ingreso" @click.prevent="onSubmitIngreso" color="secondary" />
                </q-card-actions>

            </q-card>
        </q-dialog>

    </q-page>
</template>

<style lang="scss">
// Variables de colores y espaciado
$border-color: #e0e0e0;
$section-bg: #f9f9f9;

// Estilos de secciones
.section-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1976d2;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 8px 0;
    border-bottom: 2px solid #1976d2;
    margin-bottom: 12px;
}

// Caja de información
.info-box {
    background-color: $section-bg;
    border-left: 4px solid #1976d2;
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 12px;
}

// Mejora general de formularios
:deep(.q-field__control) {
    min-height: 40px;
}

:deep(.q-field__native) {
    padding: 8px 12px;
}

// Estilos para el diálogo
:deep(.q-dialog__inner) {
    padding: 0;
}

:deep(.q-card) {
    box-shadow: 0 7px 24px rgba(0, 0, 0, 0.15);
}

:deep(.q-linear-progress) {
    height: 3px;
}
:deep(.add-visible-button) {
  position: relative;
}

@media (max-width: 600px) {
  :deep(.add-visible-button) {
    display: flex;
    justify-content: center;
  }
}

</style>

<script setup>
// Importacion de librerias
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from 'src/boot/axios'
import { ability } from 'src/services/ability'
import { useAuthStore } from 'src/stores/auth'
import Swal from 'sweetalert2'
import * as XLSX from 'xlsx'

// Constantes
const path = 'core/inventario/'
const auth = useAuthStore()

// Declaracion de variables
const toolbar = ref(false)
const uuid = ref(null)
const codigo = ref(null)
const nombre = ref(null)
const descripcion = ref(null)
const observaciones = ref(null)
const proveedor = ref(null)
const fecha = ref(null)
const numero_factura = ref(null)
const cantidad = ref(0)
const precio_unitario = ref(0)
const categoria = ref(null)
const estado = ref('AC')
const estadoOptions = ref([
    { label: 'Activo', value: 'AC' },
    { label: 'Inactivo', value: 'IN' }
])

const categoriaOptions = ref([])
const columns = ref([ 
    { name: 'codigo', align: 'center', label: 'Código', field: 'codigo', sortable: true },
    { name: 'nombre', align: 'center', label: 'Nombre', field: 'nombre', sortable: true },
    { name: 'descripcion', align: 'center', label: 'Descripción', field: 'descripcion', sortable: true },
    { name: 'observaciones', align: 'center', label: 'Observaciones', field: 'observaciones', sortable: false },
    { name: 'proveedor', align: 'center', label: 'Proveedor', field: row => row.proveedor ? row.proveedor.nombre : '', sortable: true },
    { name: 'cantidad', align: 'center', label: 'Cantidad', field: 'cantidad', sortable: true },
    { name: 'valor_ingreso', align: 'center', label: 'Valor de Ingreso', field: 'valor_ingreso', sortable: true },
    { name: 'numero_factura', align: 'center', label: 'N° Factura', field: 'numero_factura', sortable: true },
    { name: 'fecha', align: 'center', label: 'Fecha', field: 'fecha', sortable: true },
    { name: 'precio_unitario', align: 'center', label: 'Precio Unitario', field: 'precio_unitario', sortable: true },
    { name: 'valor_total', align: 'center', label: 'Valor Total', field: 'valor_total', sortable: true },
    { name: 'categoria', align: 'center', label: 'Categoría', field: 'categoria', sortable: true },
    { name: 'estado', align: 'center', label: 'Estado', field: 'estado', sortable: true }
])

// Variables para ingreso (registro de entradas)
const ingresoToolbar = ref(false)
const ingresoUuid = ref(null)
const ingresoCantidad = ref(0)
const ingresoFecha = ref(null)
const ingresoDisponibilidad = ref(0)
const ingresoNumeroFactura = ref(null)
const ingresoValorIngreso = ref(0)
const ingresoProveedor = ref(null)
const ingresoObservaciones = ref(null)
const proveedores = ref([])
const data = ref([])
const filter = ref(null)
const isEditing = ref(false)
const visible = ref(false)
const form_ref = ref(null)
const form_ingreso_ref = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })
const loadingOnSubmit = ref(false)

onMounted(() => {
    loadTable()
    setColumns()
    loadProveedores()
    loadCategorias()
    if (auth.rol === 'AD') {
        ability.update([
            { action: 'manage', subject: 'all' }
        ])
    }
    const handler = () => loadTable()
    window.addEventListener('inventario-updated', handler)
    // cleanup when component unmounts
    try { onUnmounted(() => { window.removeEventListener('inventario-updated', handler) }) } catch (e) {}
})

// Funciones
function setColumns() {
    // Insert dynamic action columns
    if (ability.can('update', 'Inventario')) {
        columns.value.push({ name: 'agregar', align: 'center', label: 'Agregar', field: 'agregar', sortable: false })
        columns.value.push({ name: 'edit', align: 'center', label: 'Editar', field: 'edit', sortable: false })
    }
    if (ability.can('delete', 'Inventario')) {
        columns.value.push({ name: 'delete', align: 'center', label: 'Eliminar', field: 'delete', sortable: false })
    }
}

function formatCurrency(value) {
    if (!value) return '$0.00'
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 2
    }).format(value)
}

async function onSubmit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    try {
        await api.post(path, {
            codigo: codigo.value,
            nombre: nombre.value,
            descripcion: descripcion.value,
            observaciones: observaciones.value,
            proveedor: proveedor.value,
            cantidad: cantidad.value,
            valor_ingreso: precio_unitario.value,
            numero_factura: null,
            fecha: null,
            precio_unitario: precio_unitario.value,
            categoria: categoria.value,
            estado: estado.value
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al guardar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo guardar el producto.",
            icon: "error"
        })
    } finally {
        loadingOnSubmit.value = false
    }
}

async function loadTable() {
    visible.value = true
    try {
        const response = await api.get(path)
        data.value = response.data
    } catch (error) {
        console.error('Error al cargar la tabla:', error)
    } finally {
        visible.value = false
    }
}

async function onEdit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    try {
        await api.put(path + uuid.value + '/', {
            codigo: codigo.value,
            nombre: nombre.value,
            descripcion: descripcion.value,
            observaciones: observaciones.value,
            proveedor: proveedor.value,
            cantidad: cantidad.value,
            valor_ingreso: precio_unitario.value,
            numero_factura: null,
            fecha: null,
            precio_unitario: precio_unitario.value,
            categoria: categoria.value,
            estado: estado.value
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al editar:', error)
        Swal.fire({
            title: "Error",
            text: "No se pudo actualizar el producto.",
            icon: "error"
        })
    } finally {
        loadingOnSubmit.value = false
    }
}

async function onDelete(row) {
    try {
        const result = await Swal.fire({
            title: "¿Está seguro?",
            text: "No podrá revertir esta acción",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        })

        if (result.isConfirmed) {
            try {
                await api.delete(path + row.uuid + '/')

                await Swal.fire({
                    title: "¡Eliminado!",
                    text: "El registro ha sido eliminado correctamente.",
                    icon: "success"
                })

                loadTable()
            } catch (apiError) {
                const detail = apiError?.response?.data?.detalle
                Swal.fire({
                    title: "Error",
                    text: detail || "No se pudo eliminar el registro. Por favor, inténtelo de nuevo.",
                    icon: "error"
                })
                console.error('Error al eliminar:', apiError)
            }
        }
    } catch (error) {
        console.error('Error general en onDelete:', error)
    }
}

function onReset() {
    uuid.value = null
    codigo.value = null
    nombre.value = null
    descripcion.value = null
    observaciones.value = null
    proveedor.value = null
    fecha.value = null
    numero_factura.value = null
    cantidad.value = 0
    precio_unitario.value = 0
    categoria.value = null
    estado.value = 'AC'
}

function creating() {
    onReset()
    isEditing.value = false
    toolbar.value = true
}

function editing(row) {
    onReset()
    isEditing.value = true
    uuid.value = row.uuid
    codigo.value = row.codigo
    nombre.value = row.nombre
    descripcion.value = row.descripcion
    observaciones.value = row.observaciones
    proveedor.value = row.proveedor ? row.proveedor.uuid : null
    cantidad.value = row.cantidad
    precio_unitario.value = row.precio_unitario
    categoria.value = row.categoria
    estado.value = row.estado
    toolbar.value = true
}

async function loadProveedores() {
    try {
        const r = await api.get('core/proveedor/')
        proveedores.value = r.data
    } catch (err) {
        console.error('Error cargando proveedores', err)
    }
}

async function loadCategorias() {
    try {
        const r = await api.get('core/categoria/')
        // map to { label, value } where value is the category name (string)
        categoriaOptions.value = r.data.map(c => ({ label: c.nombre, value: c.nombre }))
    } catch (err) {
        console.error('Error cargando categorias', err)
        // fallback to a minimal set if API fails
        categoriaOptions.value = [
            { label: 'CORTE', value: 'CORTE' },
            { label: 'CONFECCIÓN', value: 'CONFECCIÓN' },
        ]
    }
}

function openIngreso(row) {
    ingresoUuid.value = row.uuid
    ingresoCantidad.value = 0
    ingresoFecha.value = new Date().toISOString().slice(0, 10)
    ingresoDisponibilidad.value = row.cantidad || 0
    ingresoNumeroFactura.value = null
    ingresoValorIngreso.value = 0
    ingresoProveedor.value = row.proveedor ? row.proveedor.uuid : null
    ingresoObservaciones.value = null
    ingresoToolbar.value = true
}

async function onSubmitIngreso() {
    const success = form_ingreso_ref.value ? await form_ingreso_ref.value.validate() : true
    if (!success) return
    if (!ingresoCantidad.value || ingresoCantidad.value <= 0) {
        Swal.fire({ title: 'Error', text: 'La cantidad debe ser mayor a 0', icon: 'error' })
        return
    }

    try {
        await api.post(path + ingresoUuid.value + '/ingresos/', {
            cantidad: ingresoCantidad.value,
            fecha: ingresoFecha.value,
            numero_factura: ingresoNumeroFactura.value,
            valor_ingreso: ingresoValorIngreso.value,
            proveedor: ingresoProveedor.value,
            observaciones: ingresoObservaciones.value
        })
        ingresoToolbar.value = false
        await Swal.fire({ title: 'Éxito', text: 'Ingreso registrado correctamente', icon: 'success' })
        loadTable()
    } catch (error) {
        console.error('Error al registrar ingreso:', error)
        Swal.fire({ title: 'Error', text: 'No se pudo registrar el ingreso', icon: 'error' })
    }
}

function getVisibleRows() {
    let rows = data.value || []
    const f = filter.value ? String(filter.value).toLowerCase() : null
    if (f) {
        rows = rows.filter(r => {
            return Object.values(r).some(v => (v !== null && v !== undefined) && String(v).toLowerCase().includes(f))
        })
    }
    const { page, rowsPerPage } = pagination.value || { page: 1, rowsPerPage: 0 }
    if (!rowsPerPage || rowsPerPage === 0) return rows
    const start = (page - 1) * rowsPerPage
    return rows.slice(start, start + rowsPerPage)
}

async function downloadExcel() {
    const rows = getVisibleRows()
    if (!rows.length) {
        Swal.fire({ title: 'No hay datos', text: 'No hay registros para descargar', icon: 'info' })
        return
    }

    const headers = columns.value.map(c => ({ key: c.field || c.name, label: c.label }))
    const sheetData = rows.map(r => {
        const obj = {}
        headers.forEach(h => {
            const key = h.key
            const value = (r[key] !== undefined && r[key] !== null) ? (typeof r[key] === 'object' ? (r[key].nombre || JSON.stringify(r[key])) : r[key]) : ''
            obj[h.label] = value
        })
        return obj
    })

    const ws = XLSX.utils.json_to_sheet(sheetData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Inventario')
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { type: 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const date = new Date().toISOString().slice(0,10)
    a.download = `inventario_${date}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
}
</script>
