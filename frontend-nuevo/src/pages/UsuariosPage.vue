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
                        title="Usuarios" :filter="filter" row-key="name" >
                        

                        <!-- problema de permiso: (Solucionado-> dentro de una etiqueta template se debia indicar donde renderizar el componente) --> 
                        <template v-slot:top-left>
                            <Can I="create" an="Usuarios">
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
                                <q-td key="username" :props="props">
                                    {{ props.row.username }}
                                </q-td>

                                <q-td key="first_name" :props="props">
                                    {{ props.row.first_name }}
                                </q-td>

                                <q-td key="last_name" :props="props">
                                    {{ props.row.last_name }}
                                </q-td>

                                <q-td key="email" :props="props">
                                    {{ props.row.email }}
                                </q-td>

                                <q-td v-if="props.row.rol" key="rol" :props="props">
                                    {{ props.row.rol.descripcion }}
                                </q-td>

                                <q-td v-else key="rol-vacio" :props="props">
                                </q-td> <!--  (Comprobar que no se necesita y luego eliminar)-->

                                <Can I="update" an="Usuarios">
                                    <q-td key="edit" :props="props">
                                        <q-btn round size="xs" color="primary" icon="border_color"
                                            v-on:click="editing(props.row)" />
                                    </q-td>
                                </Can>

                                <Can I="delete" an="Usuarios">
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
        </div>

        <q-dialog v-model="toolbar" persistent>
            <q-card style="width: 700px; max-width: 80vw;">
                <q-card-section class="row items-center">
                    <div class="text-h6">Usuario</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-banner class="bg-grey-3">
                    <template v-slot:avatar>
                        <q-icon name="warning" color="warning" />
                    </template>
                    Los campos marcados con (*) son obligatorios
                </q-banner>

                <q-card-section>
                    <q-form ref="form_ref" @submit.prevent="onSubmit">
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-input filled v-model="username" label="Usuario *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="first_name" label="Nombres *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-5">
                                <q-input filled v-model="last_name" label="Apellidos *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                            <div class="col-md-5">
                                <q-input filled v-model="email" label="Correo electrónico *" lazy-rules
                                    :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
                            </div>
                        </div>
                        <div class="row justify-around">
                            <div class="col-md-11">
                                <q-select use-input input-debounce="0" @filter="filterFnRoles" filled v-model="rol"
                                    :options="filterOptionsRoles" option-label="descripcion" option-value="codigo"
                                    label="Rol *" emit-value map-options lazy-rules
                                    :rules="[val => !!val || 'El campo es obligatorio']" />
                            </div>
                        </div>
                    </q-form>
                </q-card-section>

                <div class="row justify-between">
                    <q-card-actions align="left" class="bg-white text-teal">
                        <q-btn v-if="isEditing" label="Enviar contraseña" @click.prevent="onSendPassword"
                            color="info" />
                    </q-card-actions>
                    <q-card-actions align="right" class="bg-white text-teal">
                        <q-btn v-if="!isEditing" label="Guardar" @click.prevent="onSubmit" color="primary" />
                        <q-btn v-else label="Actualizar" @click.prevent="onEdit" color="primary" />
                        <q-btn label="Cancelar" v-close-popup color="negative" />
                    </q-card-actions>
                </div>

            </q-card>
        </q-dialog>

    </q-page>
</template>

<style lang="scss"></style>

<script setup>
// Importacion de librerias
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { ability } from 'src/services/ability'
// import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

// Constantes
const path = 'seguridad/usuarios/'
//const $q = useQuasar()
const auth = useAuthStore()
import Swal from 'sweetalert2'

// Declaracion de variables
const toolbar = ref(false)
const uuid = ref(null)
const username = ref(null)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)
const optionsRoles = ref([])
const filterOptionsRoles = ref([])
const rol = ref(null)
const columns = ref([
    { name: 'username', align: 'center', label: 'Usuario', field: 'username', sortable: true },
    { name: 'first_name', align: 'center', label: 'Nombres', field: 'first_name', sortable: true },
    { name: 'last_name', align: 'center', label: 'Apellidos', field: 'last_name', sortable: true },
    { name: 'email', align: 'center', label: 'Correo electrónico', field: 'email', sortable: true },
    { name: 'rol', align: 'center', label: 'Rol', field: 'rol', sortable: true }
])
const data = ref([])
const filter = ref(null)
const isEditing = ref(false)
const visible = ref(false)
// const confirm = ref(false)
const form_ref = ref(null)
const pagination = ref({ page: 1, rowsPerPage: 10 })
const loadingRoles = ref(false) // Loading para el select de roles
const loadingOnSubmit = ref(false) // Loading para el submit del formulario

onMounted(() => {
    loadTable()
    loadSelectRoles()
    setColumns()
    if (auth.rol === 'AD') {
        ability.update([
            { action: 'manage', subject: 'all' }
        ])
    }

})

// Funciones
async function loadSelectRoles() {
    loadingRoles.value = true
    
    try {
        const response = await api.get(path + 'roles/')
        optionsRoles.value = response.data
        filterOptionsRoles.value = response.data
    } catch (error) {
        console.error('Error al cargar roles:', error)
    } finally {
        loadingRoles.value = false
    }
}

function setColumns() {
    if (ability.can('update', 'Usuarios')) {
        columns.value.push({ name: 'edit', align: 'center', label: 'Editar', field: 'edit', sortable: true })
    }
    if (ability.can('delete', 'Usuarios')) {
        columns.value.push({ name: 'delete', align: 'center', label: 'Eliminar', field: 'delete', sortable: true })
    }
}

function filterFnRoles(val, update) {
    if (val === '') {
        update(() => {
            filterOptionsRoles.value = optionsRoles.value
        })
        return
    }
    update(() => {
        const needle = val.toLowerCase()
        filterOptionsRoles.value = optionsRoles.value.filter(v => v.descripcion.toLowerCase().indexOf(needle) > -1)
    })
}

async function onSubmit() {
    const success = await form_ref.value.validate()
    if (!success) return

    loadingOnSubmit.value = true

    // Con el try/catch me aseguro de dar manejo de errores 
    try {
        await api.post(path, {
            username: username.value,
            first_name: first_name.value,
            last_name: last_name.value,
            email: email.value,
            rol: rol.value
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al guardar:', error)
        // Aquí agrego mensajes al usuario (dependiendo)
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
            username: username.value,
            first_name: first_name.value,
            last_name: last_name.value,
            email: email.value,
            rol: auth.rol
        })
        toolbar.value = false
        loadTable()
    } catch (error) {
        console.error('Error al editar:', error)
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
    });

    if (result.isConfirmed) {
      try {
        // Intentar eliminar el registro
        await api.delete(path + row.uuid + '/');
        
        // Mostrar mensaje de éxito
        await Swal.fire({
          title: "¡Eliminado!",
          text: "El registro ha sido eliminado correctamente.",
          icon: "success"
        });
        
        // Recargar la tabla
        loadTable();
      } catch (apiError) {
        // Si hay un error en la API, mostrar mensaje de error
        Swal.fire({
          title: "Error",
          text: "No se pudo eliminar el registro. Por favor, inténtelo de nuevo.",
          icon: "error"
        });
        console.error('Error al eliminar:', apiError);
      }
    }
  } catch (error) {
    console.error('Error general en onDelete:', error);
  }
}


function onReset() {
    username.value = null
    first_name.value = null
    last_name.value = null
    email.value = null
    rol.value = null
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
    username.value = row.username
    first_name.value = row.first_name
    last_name.value = row.last_name
    email.value = row.email
    if (row.rol) {
        rol.value = row.rol.codigo
    }
    toolbar.value = true
}

async function onSendPassword() {
    try {
        await api.get('seguridad/usuarios/generar_clave/' + uuid.value + '/')
        toolbar.value = false
    } catch (error) {
        console.error('Error al enviar contraseña:', error)
    }

}
</script>
