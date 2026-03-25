<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-lg">
      <!-- Proveedores -->
      <div class="col-xs-12 col-sm-4">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">Proveedores</div>
          </q-card-section>

          <q-card-section>
            <q-btn unelevated rounded icon="add" color="primary" @click="creatingProveedor" label="Agregar" class="q-mb-md" />
            <q-input dense debounce="300" v-model="filterProveedor" placeholder="Buscar" class="q-mb-md">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-table dense :rows="proveedores" :columns="proveedorColumns" :loading="loadingProveedor" :filter="filterProveedor" row-key="uuid" flat bordered>
              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
                  <q-td key="acciones" :props="props">
                    <q-btn round size="xs" color="primary" icon="border_color" @click="editingProveedor(props.row)" />
                    <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteProveedor(props.row)" />
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>

      <!-- Categorías -->
      <div class="col-xs-12 col-sm-4">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">Categorías</div>
          </q-card-section>

          <q-card-section>
            <q-btn unelevated rounded icon="add" color="primary" @click="creatingCategoria" label="Agregar" class="q-mb-md" />
            <q-input dense debounce="300" v-model="filterCategoria" placeholder="Buscar" class="q-mb-md">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-table dense :rows="categorias" :columns="categoriaColumns" :loading="loadingCategoria" :filter="filterCategoria" row-key="uuid" flat bordered>
              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
                  <q-td key="acciones" :props="props">
                    <q-btn round size="xs" color="primary" icon="border_color" @click="editingCategoria(props.row)" />
                    <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteCategoria(props.row)" />
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>

      <!-- Clientes -->
      <div class="col-xs-12 col-sm-4">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">Clientes</div>
          </q-card-section>

          <q-card-section>
            <q-btn unelevated rounded icon="add" color="primary" @click="creatingCliente" label="Agregar" class="q-mb-md" />
            <q-input dense debounce="300" v-model="filterCliente" placeholder="Buscar" class="q-mb-md">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-table dense :rows="clientes" :columns="clienteColumns" :loading="loadingCliente" :filter="filterCliente" row-key="uuid" flat bordered>
              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
                  <q-td key="acciones" :props="props">
                    <q-btn round size="xs" color="primary" icon="border_color" @click="editingCliente(props.row)" />
                    <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteCliente(props.row)" />
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Dialog Proveedor -->
    <q-dialog v-model="proveedorDialog" persistent>
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editingProveedorId ? 'Editar' : 'Crear' }} Proveedor</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-form ref="proveedorForm" @submit.prevent="submitProveedor">
            <q-input filled v-model="proveedorNombre" label="Nombre *" lazy-rules :rules="[val => !!val || 'El campo es obligatorio']" />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancelar" v-close-popup color="negative" flat />
          <q-btn label="Guardar" @click="submitProveedor" color="primary" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dialog Categoría -->
    <q-dialog v-model="categoriaDialog" persistent>
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editingCategoriaId ? 'Editar' : 'Crear' }} Categoría</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-form ref="categoriaForm" @submit.prevent="submitCategoria">
            <q-input filled v-model="categoriaNombre" label="Nombre *" lazy-rules :rules="[val => !!val || 'El campo es obligatorio']" />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancelar" v-close-popup color="negative" flat />
          <q-btn label="Guardar" @click="submitCategoria" color="primary" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dialog Cliente -->
    <q-dialog v-model="clienteDialog" persistent>
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editingClienteId ? 'Editar' : 'Crear' }} Cliente</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-form ref="clienteForm" @submit.prevent="submitCliente">
            <q-input filled v-model="clienteNombre" label="Nombre *" lazy-rules :rules="[val => !!val || 'El campo es obligatorio']" />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancelar" v-close-popup color="negative" flat />
          <q-btn label="Guardar" @click="submitCliente" color="primary" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

// Proveedor state
const proveedores = ref([])
const loadingProveedor = ref(false)
const filterProveedor = ref('')
const proveedorDialog = ref(false)
const proveedorNombre = ref('')
const editingProveedorId = ref(null)
const proveedorForm = ref(null)

// Categoría state
const categorias = ref([])
const loadingCategoria = ref(false)
const filterCategoria = ref('')
const categoriaDialog = ref(false)
const categoriaNombre = ref('')
const editingCategoriaId = ref(null)
const categoriaForm = ref(null)

// Cliente state
const clientes = ref([])
const loadingCliente = ref(false)
const filterCliente = ref('')
const clienteDialog = ref(false)
const clienteNombre = ref('')
const editingClienteId = ref(null)
const clienteForm = ref(null)

const proveedorColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

const categoriaColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

const clienteColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

onMounted(() => {
  loadProveedores()
  loadCategorias()
  loadClientes()
})

// Proveedor functions
async function loadProveedores() {
  loadingProveedor.value = true
  try {
    const r = await api.get('core/proveedor/')
    proveedores.value = r.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingProveedor.value = false
  }
}

function creatingProveedor() {
  proveedorNombre.value = ''
  editingProveedorId.value = null
  proveedorDialog.value = true
}

function editingProveedor(row) {
  proveedorNombre.value = row.nombre
  editingProveedorId.value = row.uuid
  proveedorDialog.value = true
}

async function submitProveedor() {
  if (!proveedorNombre.value) return
  try {
    if (editingProveedorId.value) {
      await api.put(`core/proveedor/${editingProveedorId.value}/`, { nombre: proveedorNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Proveedor actualizado', icon: 'success' })
    } else {
      await api.post('core/proveedor/', { nombre: proveedorNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Proveedor creado', icon: 'success' })
    }
    proveedorDialog.value = false
    await loadProveedores()
  } catch (err) {
    Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo guardar', icon: 'error' })
  }
}

async function deleteProveedor(row) {
  Swal.fire({
    title: '¿Está seguro?',
    text: `¿Desea eliminar el proveedor ${row.nombre}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d32f2f',
    cancelButtonColor: '#424242'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        await api.delete(`core/proveedor/${row.uuid}/`)
        Swal.fire({ title: 'Éxito', text: 'Proveedor eliminado', icon: 'success' })
        await loadProveedores()
      } catch (err) {
        Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo eliminar', icon: 'error' })
      }
    }
  })
}

// Categoría functions
async function loadCategorias() {
  loadingCategoria.value = true
  try {
    const r = await api.get('core/categoria/')
    categorias.value = r.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingCategoria.value = false
  }
}

function creatingCategoria() {
  categoriaNombre.value = ''
  editingCategoriaId.value = null
  categoriaDialog.value = true
}

function editingCategoria(row) {
  categoriaNombre.value = row.nombre
  editingCategoriaId.value = row.uuid
  categoriaDialog.value = true
}

async function submitCategoria() {
  if (!categoriaNombre.value) return
  try {
    if (editingCategoriaId.value) {
      await api.put(`core/categoria/${editingCategoriaId.value}/`, { nombre: categoriaNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Categoría actualizada', icon: 'success' })
    } else {
      await api.post('core/categoria/', { nombre: categoriaNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Categoría creada', icon: 'success' })
    }
    categoriaDialog.value = false
    await loadCategorias()
  } catch (err) {
    Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo guardar', icon: 'error' })
  }
}

async function deleteCategoria(row) {
  Swal.fire({
    title: '¿Está seguro?',
    text: `¿Desea eliminar la categoría ${row.nombre}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d32f2f',
    cancelButtonColor: '#424242'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        await api.delete(`core/categoria/${row.uuid}/`)
        Swal.fire({ title: 'Éxito', text: 'Categoría eliminada', icon: 'success' })
        await loadCategorias()
      } catch (err) {
        Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo eliminar', icon: 'error' })
      }
    }
  })
}

// Cliente functions
async function loadClientes() {
  loadingCliente.value = true
  try {
    const r = await api.get('core/cliente/')
    clientes.value = r.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingCliente.value = false
  }
}

function creatingCliente() {
  clienteNombre.value = ''
  editingClienteId.value = null
  clienteDialog.value = true
}

function editingCliente(row) {
  clienteNombre.value = row.nombre
  editingClienteId.value = row.uuid
  clienteDialog.value = true
}

async function submitCliente() {
  if (!clienteNombre.value) return
  try {
    if (editingClienteId.value) {
      await api.put(`core/cliente/${editingClienteId.value}/`, { nombre: clienteNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Cliente actualizado', icon: 'success' })
    } else {
      await api.post('core/cliente/', { nombre: clienteNombre.value })
      Swal.fire({ title: 'Éxito', text: 'Cliente creado', icon: 'success' })
    }
    clienteDialog.value = false
    await loadClientes()
  } catch (err) {
    Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo guardar', icon: 'error' })
  }
}

async function deleteCliente(row) {
  Swal.fire({
    title: '¿Está seguro?',
    text: `¿Desea eliminar el cliente ${row.nombre}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d32f2f',
    cancelButtonColor: '#424242'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        await api.delete(`core/cliente/${row.uuid}/`)
        Swal.fire({ title: 'Éxito', text: 'Cliente eliminado', icon: 'success' })
        await loadClientes()
      } catch (err) {
        Swal.fire({ title: 'Error', text: err?.response?.data?.detail || 'No se pudo eliminar', icon: 'error' })
      }
    }
  })
}
</script>

<style scoped>
</style>
