<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h5>Clientes</h5>
      </div>
      <div class="col-auto">
        <q-btn color="primary" label="Agregar Cliente" icon="add" @click="creatingCliente()" />
      </div>
    </div>

    <q-card>
      <q-card-section>
        <q-input dense debounce="300" v-model="filterCliente" placeholder="Buscar cliente" class="q-mb-md">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-table dense :rows="clientes" :columns="clienteColumns" :loading="loadingCliente" :filter="filterCliente" row-key="uuid" flat bordered>
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
              <q-td key="acciones" :props="props">
                <q-btn round size="xs" color="primary" icon="border_color" @click="editingCliente(props.row)" v-ripple title="Editar" />
                <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteCliente(props.row)" v-ripple title="Eliminar" />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

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

const clientes = ref([])
const loadingCliente = ref(false)
const filterCliente = ref('')
const clienteDialog = ref(false)
const clienteNombre = ref('')
const editingClienteId = ref(null)
const clienteForm = ref(null)

const clienteColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

onMounted(() => {
  loadClientes()
})

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
