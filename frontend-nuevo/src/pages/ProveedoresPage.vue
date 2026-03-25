<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h5>Proveedores</h5>
      </div>
      <div class="col-auto">
        <q-btn color="primary" label="Agregar Proveedor" icon="add" @click="creatingProveedor()" />
      </div>
    </div>

    <q-card>
      <q-card-section>
        <q-input dense debounce="300" v-model="filterProveedor" placeholder="Buscar proveedor" class="q-mb-md">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-table dense :rows="proveedores" :columns="proveedorColumns" :loading="loadingProveedor" :filter="filterProveedor" row-key="uuid" flat bordered>
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
              <q-td key="acciones" :props="props">
                <q-btn round size="xs" color="primary" icon="border_color" @click="editingProveedor(props.row)" v-ripple title="Editar" />
                <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteProveedor(props.row)" v-ripple title="Eliminar" />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

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
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

const proveedores = ref([])
const loadingProveedor = ref(false)
const filterProveedor = ref('')
const proveedorDialog = ref(false)
const proveedorNombre = ref('')
const editingProveedorId = ref(null)
const proveedorForm = ref(null)

const proveedorColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

onMounted(() => {
  loadProveedores()
})

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
</script>
