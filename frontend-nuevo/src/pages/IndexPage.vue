<template>
  <q-page class="q-pa-md">
    <!-- Header -->
    <div class="q-mb-lg">
      <h4 class="q-my-none">Dashboard</h4>
      <p class="text-subtitle2 text-grey">Bienvenido a UNOA - Resumen de tu aplicación</p>
    </div>

    <!-- Stats principales -->
    <div class="row q-col-gutter-md q-mb-lg">
      <!-- Inventario Total -->
      <div class="col-xs-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-blue-1">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-grey-8">Inventario Total</div>
                <div class="text-h5 text-primary q-mt-sm">{{ totalInventario }}</div>
                <div class="text-caption text-grey">Ítems en stock</div>
              </div>
              <div class="col-auto">
                <q-icon name="inventory_2" size="42px" color="primary" class="opacity-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Bajo Stock -->
      <div class="col-xs-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-orange-1">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-grey-8">Bajo Stock</div>
                <div class="text-h5 text-orange q-mt-sm">{{ bajoStock }}</div>
                <div class="text-caption text-grey">Requieren reorden</div>
              </div>
              <div class="col-auto">
                <q-icon name="warning" size="42px" color="orange" class="opacity-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Programaciones Pendientes -->
      <div class="col-xs-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-green-1">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-grey-8">Programaciones</div>
                <div class="text-h5 text-green q-mt-sm">{{ programacionesPendientes }}</div>
                <div class="text-caption text-grey">Pendientes</div>
              </div>
              <div class="col-auto">
                <q-icon name="calendar_month" size="42px" color="green" class="opacity-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Cortes en Proceso -->
      <div class="col-xs-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-purple-1">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-grey-8">Cortes</div>
                <div class="text-h5 text-purple q-mt-sm">{{ cortesEnProceso }}</div>
                <div class="text-caption text-grey">En proceso</div>
              </div>
              <div class="col-auto">
                <q-icon name="content_cut" size="42px" color="purple" class="opacity-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Secciones detalladas -->
    <div class="row q-col-gutter-md q-mb-lg">
      <!-- Últimas Programaciones -->
      <div class="col-xs-12 col-lg-6">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">Últimas Programaciones</div>
          </q-card-section>
          <q-card-section v-if="ultimasProgramaciones.length > 0">
            <q-list separator>
              <q-item v-for="prog in ultimasProgramaciones" :key="prog.uuid" class="q-py-md">
                <q-item-section avatar>
                  <q-icon name="calendar" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ prog.numero_orden }}</q-item-label>
                  <q-item-label caption>{{ prog.estado || 'Pendiente' }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip size="sm" :color="getColorEstado(prog.estado)" text-color="white">
                    {{ prog.cantidad_referencias }} ref.
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
          <q-card-section v-else class="text-center text-grey">
            <p>No hay programaciones registradas</p>
          </q-card-section>
        </q-card>
      </div>

      <!-- Últimos Cortes -->
      <div class="col-xs-12 col-lg-6">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">Últimos Cortes</div>
          </q-card-section>
          <q-card-section v-if="ultimosCortes.length > 0">
            <q-list separator>
              <q-item v-for="corte in ultimosCortes" :key="corte.uuid" class="q-py-md">
                <q-item-section avatar>
                  <q-icon name="content_cut" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ corte.orden_produccion }}</q-item-label>
                  <q-item-label caption>{{ corte.tela }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip size="sm" :color="getColorEstadoCorte(corte.estado)" text-color="white">
                    {{ corte.estado }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
          <q-card-section v-else class="text-center text-grey">
            <p>No hay cortes registrados</p>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Lavandería -->
    <div class="row q-col-gutter-md">
      <!-- Salidas Lavandería -->
      <div class="col-xs-12 col-sm-6">
        <q-card>
          <q-card-section class="bg-accent text-white">
            <div class="text-h6">Salidas Lavandería</div>
          </q-card-section>
          <q-card-section>
            <div class="text-center q-py-md">
              <div class="text-h4 text-accent">{{ salidasLavanderia }}</div>
              <div class="text-caption text-grey">En este mes</div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Recepciones Lavandería -->
      <div class="col-xs-12 col-sm-6">
        <q-card>
          <q-card-section class="bg-info text-white">
            <div class="text-h6">Recepciones Lavandería</div>
          </q-card-section>
          <q-card-section>
            <div class="text-center q-py-md">
              <div class="text-h4 text-info">{{ recepcionesLavanderia }}</div>
              <div class="text-caption text-grey">En este mes</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'

const totalInventario = ref(0)
const bajoStock = ref(0)
const programacionesPendientes = ref(0)
const cortesEnProceso = ref(0)
const ultimasProgramaciones = ref([])
const ultimosCortes = ref([])
const salidasLavanderia = ref(0)
const recepcionesLavanderia = ref(0)

onMounted(async () => {
  await loadDashboardData()
})

async function loadDashboardData() {
  try {
    // Inventario
    const inventarioRes = await api.get('core/inventario/')
    const inventarios = inventarioRes.data
    totalInventario.value = inventarios.length
    bajoStock.value = inventarios.filter(i => (i.cantidad || 0) < 10).length

    // Programaciones
    const progRes = await api.get('core/programacion/')
    const programaciones = progRes.data
    programacionesPendientes.value = programaciones.filter(p => p.estado !== 'completado').length
    ultimasProgramaciones.value = programaciones.slice(0, 5)

    // Cortes
    const corteRes = await api.get('core/corte/')
    const cortes = corteRes.data
    cortesEnProceso.value = cortes.filter(c => c.estado !== 'completado').length
    ultimosCortes.value = cortes.slice(0, 5)

    // Lavandería
    const lavRes = await api.get('core/lavanderia/')
    const lavanderia = lavRes.data
    const hoy = new Date()
    const hace30Dias = new Date(hoy.getTime() - 30 * 24 * 60 * 60 * 1000)
    
    salidasLavanderia.value = lavanderia.filter(l => {
      const fecha = new Date(l.fecha)
      return l.tipo === 'SALIDA' && fecha >= hace30Dias
    }).length

    recepcionesLavanderia.value = lavanderia.filter(l => {
      const fecha = new Date(l.fecha)
      return l.tipo === 'RECEPCION' && fecha >= hace30Dias
    }).length
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
}

function getColorEstado(estado) {
  const estadoLower = (estado || '').toLowerCase()
  if (estadoLower.includes('pendiente')) return 'orange'
  if (estadoLower.includes('progreso')) return 'blue'
  if (estadoLower.includes('completado')) return 'green'
  return 'grey'
}

function getColorEstadoCorte(estado) {
  const estadoLower = (estado || '').toLowerCase()
  if (estadoLower.includes('inicio')) return 'blue'
  if (estadoLower.includes('proceso')) return 'orange'
  if (estadoLower.includes('completado')) return 'green'
  return 'grey'
}
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.opacity-5 {
  opacity: 0.1;
}
</style>
