<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h5>Categorías</h5>
      </div>
      <div class="col-auto">
        <q-btn color="primary" label="Agregar Categoría" icon="add" @click="creatingCategoria()" />
      </div>
    </div>

    <q-card>
      <q-card-section>
        <q-input dense debounce="300" v-model="filterCategoria" placeholder="Buscar categoría" class="q-mb-md">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-table dense :rows="categorias" :columns="categoriaColumns" :loading="loadingCategoria" :filter="filterCategoria" row-key="uuid" flat bordered>
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td key="nombre" :props="props">{{ props.row.nombre }}</q-td>
              <q-td key="acciones" :props="props">
                <q-btn round size="xs" color="primary" icon="border_color" @click="editingCategoria(props.row)" v-ripple title="Editar" />
                <q-btn round size="xs" color="negative" icon="delete_forever" @click="deleteCategoria(props.row)" v-ripple title="Eliminar" />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

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
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import Swal from 'sweetalert2'

const categorias = ref([])
const loadingCategoria = ref(false)
const filterCategoria = ref('')
const categoriaDialog = ref(false)
const categoriaNombre = ref('')
const editingCategoriaId = ref(null)
const categoriaForm = ref(null)

const categoriaColumns = [
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'acciones', label: 'Acciones', field: 'uuid', align: 'center' }
]

onMounted(() => {
  loadCategorias()
})

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
</script>
