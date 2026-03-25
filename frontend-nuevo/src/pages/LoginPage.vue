<template>
  <div
    class="login-background full-height"
    style="background-image: url('/bg-textil.jpeg'); background-size: cover; background-position: center;"
  >
    <div class="login-overlay"></div>

    <div class="window-height window-width row justify-center items-center">
      <div class="column">
        <div class="row">
          <h5 align="center" class="text-h5 text-white text-center full-width q-my-md">
            UNOA App
          </h5>
        </div>

        <div class="row">
          <q-card square bordered class="q-pa-lg shadow-1 login-card">
            <img src="/logo.png" class="login-logo" alt="Logo">

            <q-form @submit.prevent="login" ref="form_login">
              <q-card-section>
                <q-input
                  square filled clearable
                  v-model="login_form.username"
                  label="Usuario"
                  class="q-mb-sm"
                />

                <q-input
                  square filled clearable
                  v-model="login_form.password"
                  type="password"
                  label="Contraseña"
                />
              </q-card-section>

              <q-card-actions class="q-px-md">
                <q-btn
                  type="submit"
                  unelevated
                  color="primary"
                  size="lg"
                  class="full-width"
                  label="INICIAR SESIÓN"
                  :loading="loading"
                  :disable="loading"
                />
              </q-card-actions>

              <q-separator class="q-my-md" />

              <div class="text-center q-mt-md">
                <a href="#" @click="openModal()">¿Olvidaste tu contraseña?</a>
              </div>
            </q-form>

            <q-banner
              v-if="error_login"
              class="bg-negative text-white q-mt-md"
            >
              {{ error_login }}
            </q-banner>
          </q-card>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL RECUPERAR CONTRASEÑA -->
  <q-dialog v-model="modalOlvidasteContrasena" persistent>
    <q-card style="min-width: 300px">
      <q-card-section class="row items-center">
        <div class="text-h6 q-pa-md">Recuperar contraseña</div>
        <p class="text-body2 q-px-md">
          Por favor, ingrese la dirección de correo electrónico que utilizó al registrarse para que podamos enviarle una nueva contraseña.
        </p>
      </q-card-section>

      <q-card-section>
        <q-input
          v-model="email_olvidaste_contrasena"
          label="Correo electrónico"
          type="email"
          clearable
          filled
          square
          autofocus
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn elevated color="red" label="Cancelar" v-close-popup />
        <q-btn elevated color="secondary" label="Enviar enlace" :loading="loading" @click="submitReset()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
// === IMPORTS ===
import { AbilityBuilder } from '@casl/ability'
import { useAuthStore } from 'src/stores/auth';
import { useRouter } from 'vue-router';
import { ref, watch } from 'vue'
import { ability } from 'src/services/ability';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar'

// === STORE / ROUTER ===
const auth = useAuthStore()
const router = useRouter()
const $q = useQuasar()

// === VARIABLES ===
const form_login = ref(null)
const login_form = ref({ username: '', password: '' })
const loading = ref(false)
const error_login = ref('')

const modalOlvidasteContrasena = ref(false)
const email_olvidaste_contrasena = ref('')

// === LOGIN ===
async function login() {
  if (!login_form.value.username || !login_form.value.password) {
    $q.notify({
      type: 'warning',
      message: 'Por favor ingresa tu usuario y contraseña.',
      position: 'top',
    })
    return
  }

  try {
    loading.value = true
    await auth.login(login_form.value)
    router.push({ name: 'index' })
  } catch (error) {
    if (error.response && [400, 401].includes(error.response.status)) {
      error_login.value = 'Usuario o contraseña incorrectos'
    } else {
      error_login.value = 'Error de conexión'
    }
  } finally {
    loading.value = false
  }
}

// === RECUPERAR CONTRASEÑA ===
function openModal() {
  email_olvidaste_contrasena.value = ''
  modalOlvidasteContrasena.value = true
}

async function submitReset() {
  if (!email_olvidaste_contrasena.value) {
    $q.notify({ type: 'warning', message: 'Por favor ingresa tu correo.' })
    return
  }

  loading.value = true
  try {
    const response = await api.post('/seguridad/verificar_correo/', {
      email: email_olvidaste_contrasena.value
    })

    if (!response) {
      $q.notify({ type: 'negative', message: 'Error al enviar el enlace.' })
      return
    }

    $q.notify({
      type: 'positive',
      message: `Se envió la nueva contraseña a: ${email_olvidaste_contrasena.value}`,
      position: 'top',
      textColor: 'black',
      icon: 'check_circle',
    })

    modalOlvidasteContrasena.value = false
  } finally {
    loading.value = false
  }
}

// === CASL ===
watch(
  () => auth.rol,
  (newRol) => {
    const { can, rules } = new AbilityBuilder(ability.constructor)
    if (newRol === 'AD') {
      can('manage', 'all')
      can(['create', 'read', 'update', 'delete', 'detail', 'finish'], ['Usuarios'])
    }
    ability.update(rules)
  }
)

// Limpia el mensaje de error al escribir
watch([() => login_form.value.username, () => login_form.value.password], () => {
  error_login.value = ''
})
</script>

<style lang="scss">
.login-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 36, 56, 0.78); 
  z-index: 1;
}

/* Para elevar el contenido sobre el overlay */
.window-height,
.window-width,
.row,
.column {
  z-index: 2;
}

.login-card {
  width: 360px;
  border-top: 4px solid #d4af37 !important;
  background: white;
}

.login-logo {
  width: 80%;
  display: block;
  margin: 0 auto 20px auto;
}

.full-height {
  height: 100vh;
}
</style>

