<template>
  <q-layout view="hHh lpR fFf">

    <q-header elevated class="bg-primary text-white navbar-unoa">
      <q-toolbar class="navbar-toolbar">
        <div class="navbar-left">
          <q-btn dense flat round icon="menu" @click="left = !left" class="navbar-menu-btn" />
          <div class="navbar-logo">
            <q-icon name="language" size="28px" color="accent" />
            <span class="navbar-title">UNOA</span>
          </div>
        </div>

        <q-space />

        <div class="navbar-center">
          <q-item-label class="text-subtitle2">Servicio de maquinilla textil</q-item-label>
        </div>

        <q-space />

        <div class="navbar-right q-gutter-md row items-center no-wrap">
          <q-btn-dropdown flat dense rounded icon="person" color="accent" :label="full_name" label-color="white">
            <q-list style="min-width: 200px">
              <q-item clickable @click="editing" v-ripple>
                <q-item-section avatar>
                  <q-icon name="edit" color="primary" />
                </q-item-section>
                <q-item-section>Mi perfil</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable @click="logout" v-ripple>
                <q-item-section avatar>
                  <q-icon name="logout" color="negative" />
                </q-item-section>
                <q-item-section>Cerrar sesión</q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer :width="200" show-if-above v-model="left" side="left" bordered class="drawer-unoa">
      <q-scroll-area class="fit drawer-scroll">
        <q-list padding separator>
          <q-item-label header class="drawer-header">Menú Principal</q-item-label>
          
          <q-item clickable :to="{ name: 'index' }" exact v-ripple exact-active-class="drawer-active">
            <q-item-section avatar>
              <q-icon name="home" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Inicio</q-item-label>
            </q-item-section>
          </q-item>

          <Can I="read" a="'Usuarios'">
            <q-item clickable :to="{ name: 'usuarios' }" exact v-ripple exact-active-class="drawer-active">
              <q-item-section avatar>
                <q-icon name="person" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Usuarios</q-item-label>
              </q-item-section>
            </q-item>
          </Can>

          <q-item clickable :to="{ name: 'parametros' }" exact v-ripple exact-active-class="drawer-active">
            <q-item-section avatar>
              <q-icon name="settings" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Parámetros</q-item-label>
            </q-item-section>
          </q-item>

          <Can I="read" a="'Inventario'">
            <q-item clickable :to="{ name: 'inventario' }" exact v-ripple exact-active-class="drawer-active">
              <q-item-section avatar>
                <q-icon name="inventory_2" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Inventario</q-item-label>
              </q-item-section>
            </q-item>
          </Can>

          <Can I="read" a="'Programacion'">
            <q-item clickable :to="{ name: 'programacion' }" exact v-ripple exact-active-class="drawer-active">
              <q-item-section avatar>
                <q-icon name="calendar_month" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Programación</q-item-label>
              </q-item-section>
            </q-item>
          </Can>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-dialog v-model="toolbar">
      <q-card style="width: 700px; max-width: 80vw;" class="profile-card">
        <q-card-section class="row items-center bg-primary text-white">
          <div class="text-h6">Mi perfil</div>
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
          <q-form ref="form_ref">
            <div class="row justify-around">
              <div class="col-md-5">
                <q-input filled v-model="first_name" label="Nombres *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div class="col-md-5">
                <q-input filled v-model="last_name" label="Apellidos *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div class="col-md-11">
                <q-input autocomplete="off" filled v-model="email" label="Correo electrónico *" lazy-rules
                  :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
            </div>

            <div class="row justify-around">
              <div v-if="nuevo_password" class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña *"
                  lazy-rules :rules="[val => val && val.length > 0 || 'El campo es obligatorio']" />
              </div>
              <div v-else class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="actual_password" label="Contraseña" />
              </div>
              <div class="col-md-5">
                <q-input autocomplete="off" type="password" filled v-model="nuevo_password"
                  label="Nueva contraseña *" />
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="bg-white text-teal">
          <q-btn label="Actualizar" @click.prevent="onEdit" color="primary" />
          <q-btn label="Cancelar" v-close-popup color="negative" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>

</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useRouter } from 'vue-router'
import { ability } from 'src/services/ability'

const auth = useAuthStore()
const router = useRouter()

// Constante de path para la API
const path = 'seguridad/perfil/'

const left = ref(false)
const toolbar = ref(false)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)
const actual_password = ref(null)
const nuevo_password = ref(null)
const full_name = ref('')
const form_ref = ref(null)

async function logout() {
  try {
    auth.logout();
    router.push('/login');
  } catch (error) {
    console.error('Error al cerrar sesión', error);
  }
}

async function loadUser() {

  const response = await api.get(path)

  first_name.value = response.data.first_name
  last_name.value = response.data.last_name
  email.value = response.data.email
  full_name.value = first_name.value + ' ' + last_name.value
}



function editing() {

  toolbar.value = true
  actual_password.value = null
  nuevo_password.value = null
}

async function onEdit() {

  const success = await form_ref.value.validate()
  if (!success) return

  await api.put(path, {
    first_name: first_name.value,
    last_name: last_name.value,
    email: email.value,
    actual_password: actual_password.value,
    nuevo_password: nuevo_password.value
  })

  toolbar.value = false
  loadUser()
}

function setAbilities(rol) {
  if (!rol) return
  if (rol === 'AD') {
    ability.update([{
      action: 'manage',
      subject: 'all'
    }])
    
  }
  else {
    ability.update([{ action: 'read', subject: 'Usuarios' }])
  }
}

onMounted(() => {
  loadUser();
  setAbilities(auth.rol)
})

watch(() => auth.rol, rol => {
  setAbilities(rol)
})
</script>

<style lang="scss">
.cursor {
  cursor: pointer;
}

// Navbar UNOA styles
.navbar-unoa {
  background: linear-gradient(135deg, #003366 0%, #002244 100%);
  border-bottom: 3px solid #D4AF37;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  .navbar-toolbar {
    padding: 8px 16px;
  }

  .navbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .navbar-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 18px;
    letter-spacing: 1px;

    .navbar-title {
      color: #ffffff;
      font-weight: 700;
    }
  }

  .navbar-menu-btn {
    color: #ffffff;

    &:hover {
      background-color: rgba(212, 175, 55, 0.2);
    }
  }

  .navbar-center {
    color: #D4AF37;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  .navbar-right {
    .q-btn-dropdown {
      &:hover {
        background-color: rgba(212, 175, 55, 0.15);
      }
    }
  }
}

// Drawer UNOA styles
.drawer-unoa {
  background-color: #f5f5f5;
  border-right: 3px solid #D4AF37;

  .drawer-header {
    color: #003366;
    font-weight: 700;
    background-color: #f0f0f0;
    border-bottom: 2px solid #D4AF37;
  }

  .q-item {
    &:hover {
      background-color: rgba(0, 51, 102, 0.08);
    }

    &.drawer-active {
      background-color: #003366;
      color: white;
      font-weight: 600;

      .q-icon {
        color: #D4AF37;
      }

      &:before {
        left: 0;
        width: 4px;
        height: 100%;
        background-color: #C41E3A;
      }
    }
  }
}

// Profile card
.profile-card {
  border-top: 4px solid #D4AF37;
}
</style>
