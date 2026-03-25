
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'index', component: () => import('pages/IndexPage.vue'), meta: { requiresAuth: true } },
      { path: 'usuarios', name: 'usuarios', component: () => import('pages/UsuariosPage.vue'), meta: { requiresAuth: true } },
      { path: 'parametros', name: 'parametros', component: () => import('pages/ParametrosPage.vue'), meta: { requiresAuth: true } },
      { path: 'proveedores', name: 'proveedores', component: () => import('pages/ProveedoresPage.vue'), meta: { requiresAuth: true } },
      { path: 'categorias', name: 'categorias', component: () => import('pages/CategoriasPage.vue'), meta: { requiresAuth: true } },
      { path: 'clientes', name: 'clientes', component: () => import('pages/ClientesPage.vue'), meta: { requiresAuth: true } },
      { path: 'inventario', name: 'inventario', component: () => import('pages/InventarioPage.vue'), meta: { requiresAuth: true } },
      { path: 'programacion', name: 'programacion', component: () => import('pages/ProgramacionPage.vue'), meta: { requiresAuth: true } },
      { path: 'corte', name: 'corte', component: () => import('pages/CortePage.vue'), meta: { requiresAuth: true } },
      { path: 'presentacion', name: 'presentacion', component: () => import('pages/PresentacionPage.vue'), meta: { requiresAuth: true } },
      { path: 'lavanderia', name: 'lavanderia', component: () => import('pages/LavanderiaPage.vue'), meta: { requiresAuth: true } }
    ]
  },
  { path: '/login', name: 'login', component: () => import('pages/LoginPage.vue') }
]

// Always leave this as last one
if (process.env.MODE !== 'ssr') {
  routes.push({
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  })
}

export default routes

